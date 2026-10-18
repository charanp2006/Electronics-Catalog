from fastapi import APIRouter, Depends, Request

from app.core.admin_auth import client_ip, get_admin_user
from app.schemas.admin.order import OrderStatusUpdate
from app.services.admin.orders import OrderService

router = APIRouter(prefix="/orders", tags=["Admin Orders"])


@router.get("")
def list_orders(
    status: str | None = None,
    q: str | None = None,
    user_id: str | None = None,
    sort: str = "newest",
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(get_admin_user),
):
    return OrderService().list(status=status, q=q, user_id=user_id, sort=sort, page=page, limit=limit)


@router.get("/{order_id}")
def get_order(order_id: str, user: dict = Depends(get_admin_user)):
    return OrderService().get(order_id)


@router.patch("/{order_id}/status")
def set_order_status(
    order_id: str, payload: OrderStatusUpdate, request: Request, user: dict = Depends(get_admin_user)
):
    return OrderService().set_status(order_id, payload.status.value, user, client_ip(request))
