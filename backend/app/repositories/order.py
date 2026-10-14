from datetime import datetime, timezone
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongodb import get_db
from app.repositories.cart import CartRepository
from app.utils.serialization import serialize


class OrderRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["orders"]
        self.products = self.db["products"]
        self.cart = CartRepository()

    def create_from_cart(self, user_id: str) -> Dict[str, Any]:
        cart = self.cart.get_cart(user_id)
        items = cart["items"]
        if not items:
            raise HTTPException(status_code=400, detail="Your cart is empty")

        # Validate stock
        for item in items:
            product = self.products.find_one({"_id": ObjectId(item["product_id"])})
            if not product or product.get("stock", 0) < item["quantity"]:
                raise HTTPException(
                    status_code=400, detail=f"Insufficient stock for {item['name']}"
                )

        # Decrement stock
        for item in items:
            self.products.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$inc": {"stock": -item["quantity"]}},
            )

        order = {
            "user_id": user_id,
            "items": items,
            "subtotal": cart["subtotal"],
            "discount": cart["discount"],
            "total": cart["total"],
            "status": "placed",
            "created_at": datetime.now(timezone.utc),
        }
        result = self.collection.insert_one(order)
        self.cart.clear(user_id)
        order["_id"] = result.inserted_id
        return serialize(order)

    def list_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        return serialize(list(cursor))
