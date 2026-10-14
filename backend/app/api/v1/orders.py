from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.repositories.order import OrderRepository
from app.schemas.cart import OrderCreate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", status_code=201)
def create_order(_: OrderCreate | None = None, user: dict = Depends(get_current_user)):
    return OrderRepository().create_from_cart(user["_id"])


@router.get("/")
def list_orders(user: dict = Depends(get_current_user)):
    return OrderRepository().list_for_user(user["_id"])
