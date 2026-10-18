from datetime import datetime, timezone
from typing import Any, Dict

from app.db.mongodb import get_db
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class StatsService:
    def __init__(self):
        self.db = get_db()

    def overview(self) -> Dict[str, Any]:
        products = self.db["products"]
        orders = self.db["orders"]

        orders_by_status: Dict[str, int] = {}
        for row in orders.aggregate([{"$group": {"_id": "$status", "n": {"$sum": 1}}}]):
            orders_by_status[row["_id"] or "pending"] = row["n"]

        review_counts = {"published": 0, "hidden": 0}
        for row in products.aggregate(
            [
                {"$unwind": "$reviews"},
                {"$group": {"_id": {"$ifNull": ["$reviews.status", "published"]}, "n": {"$sum": 1}}},
            ]
        ):
            review_counts[row["_id"]] = row["n"]

        revenue = list(
            orders.aggregate(
                [
                    {"$match": {"status": {"$ne": "cancelled"}}},
                    {"$group": {"_id": None, "total": {"$sum": "$total"}}},
                ]
            )
        )

        recent = list(orders.find().sort("created_at", -1).limit(5))
        recent_items = []
        for order in recent:
            recent_items.append(
                {
                    "id": str(order["_id"]),
                    "total": order.get("total"),
                    "status": order.get("status", "pending"),
                    "created_at": order.get("created_at"),
                }
            )

        return serialize(
            {
                "products": {
                    "total": products.count_documents({}),
                    "active": products.count_documents({"is_active": True}),
                    "out_of_stock": products.count_documents({"stock": {"$lte": 0}}),
                    "low_stock": products.count_documents({"stock": {"$gt": 0, "$lte": 5}}),
                },
                "orders": {
                    "total": orders.count_documents({}),
                    "by_status": orders_by_status,
                    "revenue": round(revenue[0]["total"], 2) if revenue else 0,
                },
                "reviews": {
                    "total": sum(review_counts.values()),
                    "published": review_counts.get("published", 0),
                    "hidden": review_counts.get("hidden", 0),
                },
                "catalog": {
                    "categories": self.db["categories"].count_documents({}),
                    "brands": self.db["brands"].count_documents({}),
                },
                "recent_orders": recent_items,
            }
        )
