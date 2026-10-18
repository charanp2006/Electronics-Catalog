from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.mongodb import BaseRepository, get_db
from app.utils.serialization import serialize


class ProductRepository(BaseRepository):
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["products"]

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
        return serialize(doc)

    def add_review(
        self, slug: str, user: Dict[str, Any], rating: int, comment: str
    ) -> Optional[Dict[str, Any]]:
        doc = self.collection.find_one({"slug": slug})
        if not doc:
            return None
        reviews = doc.get("reviews", [])
        reviews.append(
            {
                "user_id": user["_id"],
                "username": user.get("username", "user"),
                "rating": rating,
                "comment": comment,
                "created_at": datetime.now(timezone.utc),
            }
        )
        average = round(sum(r["rating"] for r in reviews) / len(reviews), 2)
        self.collection.update_one(
            {"slug": slug},
            {
                "$set": {
                    "reviews": reviews,
                    "average_rating": average,
                    "total_reviews": len(reviews),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return self.get_by_slug(slug)

    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        from bson import ObjectId

        if not ObjectId.is_valid(product_id):
            return None
        doc = self.collection.find_one({"_id": ObjectId(product_id)})
        return serialize(doc) if doc else None

    def featured(self, limit: int = 8) -> list:
        cursor = (
            self.collection.find({"is_active": True, "is_featured": True}, {"reviews": 0, "price_history": 0})
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
