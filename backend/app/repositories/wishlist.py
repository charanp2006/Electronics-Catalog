from datetime import datetime, timezone
from typing import Any, Dict, List

from bson import ObjectId

from app.db.mongodb import BaseRepository, get_db
from app.utils.serialization import serialize

SUMMARY_PROJECTION = {"reviews": 0, "price_history": 0}


class WishlistRepository(BaseRepository):
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["wishlists"]
        self.products = self.db["products"]

    def _product_ids(self, user_id: str) -> List[str]:
        doc = self.collection.find_one({"user_id": user_id})
        return doc.get("product_ids", []) if doc else []

    def list_items(self, user_id: str) -> List[Dict[str, Any]]:
        ids = [ObjectId(i) for i in self._product_ids(user_id) if ObjectId.is_valid(i)]
        if not ids:
            return []
        cursor = self.products.find({"_id": {"$in": ids}}, SUMMARY_PROJECTION)
        items = serialize(list(cursor))
        order = {str(i): idx for idx, i in enumerate(ids)}
        items.sort(key=lambda x: order.get(x["_id"], 0))
        return items

    def _save(self, user_id: str, ids: List[str]) -> None:
        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"product_ids": ids, "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

    def add(self, user_id: str, product_id: str) -> None:
        ids = self._product_ids(user_id)
        if product_id not in ids:
            ids.append(product_id)
            self._save(user_id, ids)

    def remove(self, user_id: str, product_id: str) -> None:
        ids = [i for i in self._product_ids(user_id) if i != product_id]
        self._save(user_id, ids)
