from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.repositories.product import ProductRepository
from app.schemas.admin.review import ReviewUpdate
from app.services.admin import audit
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ReviewService:
    def __init__(self):
        self.repo = ProductRepository()

    def list(
        self,
        product_id: Optional[str] = None,
        status: Optional[str] = None,
        rating: Optional[int] = None,
        q: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if product_id and ObjectId.is_valid(product_id):
            query["_id"] = ObjectId(product_id)

        cursor = self.repo.collection.find(query, {"name": 1, "slug": 1, "reviews": 1})

        rows: List[Dict[str, Any]] = []
        for product in cursor:
            for review in product.get("reviews", []):
                status_v = review.get("status", "published")
                if status and status != status_v:
                    continue
                if rating and review.get("rating") != rating:
                    continue
                if q:
                    haystack = f"{review.get('comment', '')} {review.get('username', '')}".lower()
                    if q.lower() not in haystack:
                        continue
                rows.append(
                    {
                        "review_id": review.get("review_id"),
                        "product_id": str(product["_id"]),
                        "product_name": product.get("name"),
                        "product_slug": product.get("slug"),
                        "username": review.get("username"),
                        "user_id": review.get("user_id"),
                        "rating": review.get("rating"),
                        "comment": review.get("comment"),
                        "status": status_v,
                        "created_at": review.get("created_at"),
                        "moderated_by": review.get("moderated_by"),
                        "moderated_at": review.get("moderated_at"),
                    }
                )

        if sort == "rating":
            rows.sort(key=lambda r: r.get("rating") or 0, reverse=True)
        else:
            rows.sort(key=lambda r: r.get("created_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

        total = len(rows)
        start = (page - 1) * limit
        return {
            "items": serialize(rows[start : start + limit]),
            "total": total,
            "page": page,
            "limit": limit,
        }

    def _find(self, product_id: str, review_id: str):
        raw = self.repo.get_by_id_raw(product_id)
        if not raw:
            raise HTTPException(status_code=404, detail="Product not found")
        reviews = raw.get("reviews", [])
        for review in reviews:
            if review.get("review_id") == review_id:
                return raw, reviews, review
        raise HTTPException(status_code=404, detail="Review not found")

    def moderate(
        self, product_id: str, review_id: str, payload: ReviewUpdate, actor: dict, ip: Optional[str] = None
    ) -> dict:
        raw, reviews, review = self._find(product_id, review_id)
        now = _now()
        if payload.rating is not None:
            review["rating"] = payload.rating
        if payload.comment is not None:
            review["comment"] = payload.comment
        if payload.status is not None:
            review["status"] = payload.status
            review["moderated_by"] = (actor or {}).get("username")
            review["moderated_at"] = now
        review["updated_at"] = now

        self.repo.collection.update_one({"_id": raw["_id"]}, {"$set": {"reviews": reviews}})
        self.repo.recompute_rating(product_id)
        audit.log(actor, "review.moderate", "review", review_id, f"status={review.get('status')}", ip=ip)
        return serialize(review)

    def delete(self, product_id: str, review_id: str, actor: dict, ip: Optional[str] = None) -> dict:
        raw, reviews, _review = self._find(product_id, review_id)
        reviews = [r for r in reviews if r.get("review_id") != review_id]
        self.repo.collection.update_one({"_id": raw["_id"]}, {"$set": {"reviews": reviews}})
        self.repo.recompute_rating(product_id)
        audit.log(actor, "review.delete", "review", review_id, ip=ip)
        return {"deleted": True}
