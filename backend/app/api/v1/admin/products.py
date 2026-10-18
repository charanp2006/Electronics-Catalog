from fastapi import APIRouter, Depends, Request, status

from app.core.admin_auth import client_ip, get_admin_user
from app.schemas.admin.product import ProductPatch, ProductWrite
from app.services.admin.products import ProductService

router = APIRouter(prefix="/products", tags=["Admin Products"])


@router.get("")
def list_products(
    q: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    is_active: bool | None = None,
    is_featured: bool | None = None,
    stock: str | None = None,
    sort: str = "newest",
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(get_admin_user),
):
    return ProductService().list(
        q=q,
        category=category,
        brand=brand,
        is_active=is_active,
        is_featured=is_featured,
        stock=stock,
        sort=sort,
        page=page,
        limit=limit,
    )


@router.get("/{product_id}")
def get_product(product_id: str, user: dict = Depends(get_admin_user)):
    return ProductService().get(product_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductWrite, request: Request, user: dict = Depends(get_admin_user)):
    return ProductService().create(payload, user, client_ip(request))


@router.put("/{product_id}")
def update_product(
    product_id: str, payload: ProductWrite, request: Request, user: dict = Depends(get_admin_user)
):
    return ProductService().update(product_id, payload, user, client_ip(request))


@router.patch("/{product_id}")
def patch_product(
    product_id: str, payload: ProductPatch, request: Request, user: dict = Depends(get_admin_user)
):
    return ProductService().patch(product_id, payload.model_dump(exclude_unset=True), user, client_ip(request))


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    request: Request,
    hard: bool = False,
    user: dict = Depends(get_admin_user),
):
    return ProductService().delete(product_id, user, hard=hard, ip=client_ip(request))
