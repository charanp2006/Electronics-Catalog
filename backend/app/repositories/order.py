from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongodb import BaseRepository, get_db
from app.repositories.cart import CartRepository
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OrderRepository(BaseRepository):
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["orders"]
        self.products = self.db["products"]
        self.users = self.db["users"]
        self.cart = CartRepository()

    # ------------------------------------------------------------------ store
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
                    status_code=400, detail=f"Product out of stock: {item['name']}"
                )

        # Decrement stock
        for item in items:
            self.products.update_one(
                {"_id": ObjectId(item["product_id"])},
                {"$inc": {"stock": -item["quantity"]}},
            )

        now = _now()
        doc = {
            "user_id": user_id,
            "items": items,
            "subtotal": cart["subtotal"],
            "discount": cart["discount"],
            "total": cart["total"],
            "status": "pending",
            "status_history": [{"status": "pending", "at": now, "by": "system"}],
            "created_at": now,
            "updated_at": now,
        }
        inserted = self.collection.insert_one(doc)
        self.cart.clear(user_id)
        doc["_id"] = inserted.inserted_id
        return serialize(doc)

    def list_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        return serialize(list(cursor))

    # ------------------------------------------------------------------ admin
    def _customer(self, user_id: str) -> dict:
        if not user_id or not ObjectId.is_valid(user_id):
            return {"id": user_id, "username": None, "email": None}
        user = self.db["users"].find_one(
            {"_id": ObjectId(user_id)}, {"username": 1, "email": 1, "name": 1}
        )
        if not user:
            return {"id": user_id, "username": None, "email": None}
        return {
            "id": str(user["_id"]),
            "username": user.get("username"),
            "email": user.get("email"),
            "name": user.get("name"),
        }

    def _decorate(self, doc: dict) -> dict:
        data = serialize(doc)
        data["id"] = data.pop("_id")
        data.setdefault("status", "pending")
        data["user"] = self._customer(doc.get("user_id"))
        return data

    def list_admin(
        self,
        status: str | None = None,
        q: str | None = None,
        user_id: str | None = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        if user_id and ObjectId.is_valid(user_id):
            query["user_id"] = user_id
        if q:
            or_terms = []
            regex = {"$regex": q, "$options": "i"}
            # match customer by username/email
            ids = [
                str(u["_id"])
                for u in self.db["users"].find(
                    {"$or": [{"username": regex}, {"email": regex}]}, {"_id": 1}
                )
            ]
            or_terms.append({"user_id": {"$in": ids}})
            if ObjectId.is_valid(q):
                or_terms.append({"_id": ObjectId(q)})
            query["$or"] = or_terms

        order_by = [("total", -1)] if sort == "total" else [("created_at", -1)]
        total = self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort(order_by)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return {
            "items": [self._decorate(d) for d in cursor],
            "total": total,
            "page": page,
            "limit": limit,
        }

    def get_admin(self, order_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(order_id):
            return None
        doc = self.collection.find_one({"_id": ObjectId(order_id)})
        return self._decorate(doc) if doc else None

    def set_status(self, order_id: str, status: str, actor: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(order_id):
            return None
        now = _now()
        result = self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {"status": status, "updated_at": now},
                "$push": {"status_history": {"status": status, "at": now, "by": actor}},
            },
        )
        if result.matched_count == 0:
            return None
        return self.get_admin(order_id)
