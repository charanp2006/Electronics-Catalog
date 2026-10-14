from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.repositories.cart import CartRepository
from app.schemas.cart import CartItemAdd, CartItemUpdate

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/")
def get_cart(user: dict = Depends(get_current_user)):
    return CartRepository().get_cart(user["_id"])


@router.post("/add")
def add_to_cart(payload: CartItemAdd, user: dict = Depends(get_current_user)):
    return CartRepository().add_item(user["_id"], payload.product_id, payload.quantity)


@router.put("/update")
def update_cart(payload: CartItemUpdate, user: dict = Depends(get_current_user)):
    return CartRepository().update_item(user["_id"], payload.product_id, payload.quantity)


@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    return CartRepository().remove_item(user["_id"], product_id)


@router.delete("/clear")
def clear_cart(user: dict = Depends(get_current_user)):
    return CartRepository().clear(user["_id"])
