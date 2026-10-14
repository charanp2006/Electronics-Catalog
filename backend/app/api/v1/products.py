from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.repositories.product import ProductRepository
from app.schemas.cart import ReviewCreate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
def list_products(
    q: Optional[str] = Query(None, description="Search by name, brand, category or specs"),
    category: Optional[str] = Query(None, description="Category slug or name"),
    brand: Optional[str] = Query(None, description="Brand slug or name"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort: str = Query("newest", pattern="^(price_asc|price_desc|rating_desc|newest)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
):
    return ProductRepository().list_products(
        q, category, brand, min_price, max_price, sort, page, limit
    )


@router.get("/featured")
def featured_products(limit: int = Query(8, ge=1, le=20)):
    return ProductRepository().featured(limit)


@router.get("/{slug}")
def get_product(slug: str):
    data = ProductRepository().get_by_slug(slug)
    if not data:
        raise HTTPException(status_code=404, detail="Product not found")
    return data


@router.get("/{slug}/related")
def related_products(slug: str, limit: int = Query(4, ge=1, le=12)):
    repo = ProductRepository()
    product = repo.get_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    category_slug = (product.get("category") or {}).get("slug")
    if not category_slug:
        return []
    return repo.related(category_slug, slug, limit)


@router.post("/{slug}/reviews")
def add_review(
    slug: str,
    payload: ReviewCreate,
    user: dict = Depends(get_current_user),
):
    product = ProductRepository().add_review(slug, user, payload.rating, payload.comment)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
