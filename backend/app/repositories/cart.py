from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongodb import BaseRepository, get_db
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CartRepository(BaseRepository):
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["carts"]
        self.products = self.db["products"]

    def _load(self, user_id: str) -> Dict[str, Any]:
        doc = self.collection.find_one({"user_id": user_id})
        if not doc:
            doc = {"user_id": user_id, "items": [], "updated_at": _now()}
            doc["_id"] = self.collection.insert_one(
                {"user_id": user_id, "items": [], "updated_at": _now()}
            ).inserted_id
        doc.setdefault("items", [])
        return doc

    def _serialize(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        items = []
        subtotal = 0.0
        discount = 0.0
        count = 0
        for item in doc.get("items", []):
            price = item.get("price", 0)
            discount_price = item.get("discount_price")
            qty = item.get("quantity", 1)
            unit = discount_price if discount_price else price
            subtotal += price * qty
            if discount_price:
                discount += (price - discount_price) * qty
            count += qty
            items.append(serialize(item))
        return {
            "items": items,
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "total": round(subtotal - discount, 2),
            "count": count,
        }

    def get_cart(self, user_id: str) -> Dict[str, Any]:
        return self._serialize(self._load(user_id))

    def _product_snapshot(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "product_id": str(product["_id"]),
            "slug": product["slug"],
            "name": product["name"],
            "image": product.get("image"),
            "price": product.get("price", 0),
            "discount_price": product.get("discount_price"),
            "stock": product.get("stock", 0),
        }

    def add_item(self, user_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product id")
        product = self.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.get("stock", 0) <= 0:
            raise HTTPException(status_code=400, detail="Product is out of stock")

        doc = self._load(user_id)
        items = doc.get("items", [])
        existing = next((i for i in items if i["product_id"] == product_id), None)
        max_qty = product.get("stock", 0)
        if existing:
            existing["quantity"] = min(existing["quantity"] + quantity, max_qty)
        else:
            snapshot = self._product_snapshot(product)
            snapshot["quantity"] = min(quantity, max_qty)
            items.append(snapshot)
        self.collection.update_one(
            {"user_id": user_id}, {"$set": {"items": items, "updated_at": _now()}}
        )
        return self._serialize({"items": items})

    def update_item(self, user_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
        doc = self._load(user_id)
        items = doc.get("items", [])
        if quantity <= 0:
            items = [i for i in items if i["product_id"] != product_id]
        else:
            for item in items:
                if item["product_id"] == product_id:
                    item["quantity"] = quantity
        self.collection.update_one(
            {"user_id": user_id}, {"$set": {"items": items, "updated_at": _now()}}
        )
        return self._serialize({"items": items})

    def remove_item(self, user_id: str, product_id: str) -> Dict[str, Any]:
        doc = self._load(user_id)
        items = [i for i in doc.get("items", []) if i["product_id"] != product_id]
        self.collection.update_one(
            {"user_id": user_id}, {"$set": {"items": items, "updated_at": _now()}}
        )
        return self._serialize({"items": items})

    def clear(self, user_id: str) -> Dict[str, Any]:
        self.collection.update_one(
            {"user_id": user_id}, {"$set": {"items": [], "updated_at": _now()}}
        )
        return self._serialize({"items": []})

    def raw_items(self, user_id: str) -> List[Dict[str, Any]]:
        return self._load(user_id).get("items", [])
