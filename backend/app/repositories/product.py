from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from bson import ObjectId

from app.db.mongodb import BaseRepository, get_db
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProductRepository(BaseRepository):
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["products"]

    # ------------------------------------------------------------------ store
    def list_products(
        self,
        q: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 12,
    ) -> Dict[str, Any]:
        match: Dict[str, Any] = {"is_active": True}

        if q:
            regex = {"$regex": q, "$options": "i"}
            match["$or"] = [
                {"name": regex},
                {"description": regex},
                {"brand.name": regex},
                {"category.name": regex},
                {"specifications.value": regex},
            ]
        if category:
            match["$or"] = match.get("$or", []) + [
                {"category.slug": category},
                {"category.name": {"$regex": f"^{category}$", "$options": "i"}},
            ]
        if brand:
            match["$or"] = match.get("$or", []) + [
                {"brand.slug": brand},
                {"brand.name": {"$regex": f"^{brand}$", "$options": "i"}},
            ]

        sort_map = {
            "price_asc": [("effective_price", 1)],
            "price_desc": [("effective_price", -1)],
            "rating_desc": [("average_rating", -1)],
            "newest": [("created_at", -1)],
        }
        sort_spec = sort_map.get(sort, sort_map["newest"])

        skip = (page - 1) * limit

        pipeline: list = [
            {"$match": match},
            {"$addFields": {"effective_price": {"$ifNull": ["$discount_price", "$price"]}}},
        ]

        price_range: Dict[str, float] = {}
        if min_price is not None:
            price_range["$gte"] = min_price
        if max_price is not None:
            price_range["$lte"] = max_price
        if price_range:
            pipeline.append({"$match": {"effective_price": price_range}})

        pipeline += [
            {"$sort": dict(sort_spec)},
            {
                "$facet": {
                    "items": [
                        {"$skip": skip},
                        {"$limit": limit},
                        {"$project": {"specifications": 0, "reviews": 0, "price_history": 0}},
                    ],
                    "total": [{"$count": "count"}],
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))[0]
        total = result["total"][0]["count"] if result["total"] else 0

        return {
            "items": serialize(result["items"]),
            "total": total,
            "page": page,
            "limit": limit,
        }

    def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.find_one({"slug": slug})
        if not doc:
            return None
        doc["reviews"] = [
            r for r in doc.get("reviews", []) if r.get("status", "published") == "published"
        ]
        return serialize(doc)

    def add_review(
        self, slug: str, user: Dict[str, Any], rating: int, comment: str
    ) -> Optional[Dict[str, Any]]:
        doc = self.collection.find_one({"slug": slug})
        if not doc:
            return None
        review = {
            "review_id": uuid4().hex,
            "user_id": str(user.get("_id")),
            "username": user.get("username"),
            "rating": rating,
            "comment": comment,
            "status": "published",
            "created_at": _now(),
            "updated_at": _now(),
        }
        reviews = doc.get("reviews", []) + [review]
        self.collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"reviews": reviews, "updated_at": _now()}},
        )
        self.recompute_rating(str(doc["_id"]))
        return self.get_by_slug(doc["slug"])

    def featured(self, limit: int = 8) -> list:
        cursor = (
            self.collection.find(
                {"is_active": True, "is_featured": True}, {"reviews": 0, "price_history": 0}
            )
            .sort("average_rating", -1)
            .limit(limit)
        )
        return serialize(list(cursor))

    def related(self, category_slug: str, exclude_slug: str, limit: int = 4) -> list:
        cursor = self.collection.find(
            {"is_active": True, "category.slug": category_slug, "slug": {"$ne": exclude_slug}},
            {"reviews": 0, "price_history": 0},
        ).limit(limit)
        return serialize(list(cursor))

    # ------------------------------------------------------------------ admin
    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(product_id):
            return None
        doc = self.collection.find_one({"_id": ObjectId(product_id)})
        return serialize(doc) if doc else None

    def list_admin(
        self,
        q: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        stock: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if q:
            regex = {"$regex": q, "$options": "i"}
            query["$or"] = [
                {"name": regex},
                {"slug": regex},
                {"brand.name": regex},
                {"category.name": regex},
            ]
        if category:
            query["category.slug"] = category
        if brand:
            query["brand.slug"] = brand
        if is_active is not None:
            query["is_active"] = is_active
        if is_featured is not None:
            query["is_featured"] = is_featured
        if stock == "out":
            query["stock"] = {"$lte": 0}
        elif stock == "low":
            query["stock"] = {"$gt": 0, "$lte": 5}

        sort_map = {
            "newest": [("created_at", -1)],
            "name": [("name", 1)],
            "price": [("price", -1)],
            "stock": [("stock", 1)],
        }
        sort_spec = sort_map.get(sort, sort_map["newest"])

        total = self.collection.count_documents(query)
        cursor = (
            self.collection.find(query, {"reviews": 0, "price_history": 0})
            .sort(sort_spec)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return {"items": serialize(list(cursor)), "total": total, "page": page, "limit": limit}

    def get_by_id_raw(self, product_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(product_id):
            return None
        return self.collection.find_one({"_id": ObjectId(product_id)})

    def create(self, doc: Dict[str, Any]):
        return self.collection.insert_one(doc)

    def update(self, product_id: str, updates: Dict[str, Any]) -> int:
        if not ObjectId.is_valid(product_id):
            return 0
        result = self.collection.update_one({"_id": ObjectId(product_id)}, {"$set": updates})
        return result.matched_count

    def delete(self, product_id: str) -> int:
        if not ObjectId.is_valid(product_id):
            return 0
        result = self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count

    def recompute_rating(self, product_id: str) -> None:
        if not ObjectId.is_valid(product_id):
            return
        doc = self.collection.find_one({"_id": ObjectId(product_id)}, {"reviews": 1})
        if not doc:
            return
        published = [r for r in doc.get("reviews", []) if r.get("status", "published") == "published"]
        avg = round(sum(r.get("rating", 0) for r in published) / len(published), 2) if published else 0
        self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"average_rating": avg, "total_reviews": len(published)}},
        )
