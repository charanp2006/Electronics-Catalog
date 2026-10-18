from typing import Any, Dict, Optional

from fastapi import HTTPException

from app.repositories.order import OrderRepository
from app.services.admin import audit

ALLOWED_TRANSITIONS: Dict[str, set] = {
    "pending": {"processing", "cancelled"},
    "processing": {"shipped", "cancelled"},
    "shipped": {"delivered", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
}


class OrderService:
    def __init__(self):
        self.repo = OrderRepository()

    def list(self, **filters) -> dict:
        return self.repo.list_admin(**filters)

    def get(self, order_id: str) -> dict:
        order = self.repo.get_admin(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def set_status(self, order_id: str, status: str, actor: dict, ip: Optional[str] = None) -> dict:
        order = self.repo.get_admin(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        current = order.get("status", "pending")
        if status == current:
            return order
        if status not in ALLOWED_TRANSITIONS.get(current, set()):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition: {current} -> {status}",
            )

        username = (actor or {}).get("username") or "admin"
        updated = self.repo.set_status(order_id, status, username)
        audit.log(actor, "order.status", "order", order_id, f"{current} -> {status}", ip=ip)
        return updated
