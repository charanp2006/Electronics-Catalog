from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.repositories.wishlist import WishlistRepository
from app.schemas.cart import CartItemAdd

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("/")
def get_wishlist(user: dict = Depends(get_current_user)):
    return WishlistRepository().list_items(user["_id"])


@router.post("/add")
def add_to_wishlist(payload: CartItemAdd, user: dict = Depends(get_current_user)):
    repo = WishlistRepository()
    repo.add(user["_id"], payload.product_id)
    return repo.list_items(user["_id"])


@router.delete("/remove/{product_id}")
def remove_from_wishlist(product_id: str, user: dict = Depends(get_current_user)):
    repo = WishlistRepository()
    repo.remove(user["_id"], product_id)
    return repo.list_items(user["_id"])
