from typing import Any, Dict, List

from app.db.mongodb import BaseRepository, get_db
from app.utils.serialization import serialize


class CategoryRepository(BaseRepository):
    def __init__(self):
        self.collection = get_db()["categories"]

    def list_all(self) -> List[Dict[str, Any]]:
        items = list(self.collection.find().sort("name", 1))
        products = get_db()["products"]
        for item in items:
            item["product_count"] = products.count_documents(
                {"category.slug": item.get("slug"), "is_active": True}
            )
        return serialize(items)

    def get_by_slug(self, slug: str) -> Dict[str, Any] | None:
        return serialize(self.collection.find_one({"slug": slug}))
