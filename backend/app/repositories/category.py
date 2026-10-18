from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.db.mongodb import BaseRepository, get_db
from app.utils.serialization import serialize


class CategoryRepository(BaseRepository):
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["categories"]
        self.products = self.db["products"]

    def _with_counts(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for item in items:
            item["product_count"] = self.products.count_documents(
                {"category.slug": item.get("slug"), "is_active": True}
            )
        return serialize(items)

    def list_all(self) -> List[Dict[str, Any]]:
        return self._with_counts(list(self.collection.find().sort("name", 1)))

    def list_admin(self, q: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if q:
            query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"slug": {"$regex": q, "$options": "i"}},
            ]
        return self._with_counts(list(self.collection.find(query).sort("name", 1)))

    def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        return serialize(self.collection.find_one({"slug": slug}))

    def get_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(category_id):
            return None
        doc = self.collection.find_one({"_id": ObjectId(category_id)})
        return serialize(doc) if doc else None

    def product_count(self, slug: str) -> int:
        return self.products.count_documents({"category.slug": slug})

    def create(self, doc: Dict[str, Any]):
        return self.collection.insert_one(doc)

    def update(self, category_id: str, updates: Dict[str, Any]) -> int:
        if not ObjectId.is_valid(category_id):
            return 0
        return self.collection.update_one(
            {"_id": ObjectId(category_id)}, {"$set": updates}
        ).matched_count

    def delete(self, category_id: str) -> int:
        if not ObjectId.is_valid(category_id):
            return 0
        return self.collection.delete_one({"_id": ObjectId(category_id)}).deleted_count
