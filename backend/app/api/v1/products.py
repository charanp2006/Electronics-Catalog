from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.repositories.product import ProductRepository

router = APIRouter(prefix="/products", tags=["Products"])
repo = ProductRepository()

@router.get("/")
def list_products(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50)
):
    return repo.list_products(q, category, brand, min_price, max_price, sort, page, limit)

@router.get("/{slug}")
def get_product(slug: str):
    data = repo.get_by_slug(slug)
    if not data:
        raise HTTPException(status_code=404, detail="Product not found")
    return data
