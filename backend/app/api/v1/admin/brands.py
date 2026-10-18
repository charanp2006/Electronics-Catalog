from fastapi import APIRouter, Depends, Request, status

from app.core.admin_auth import client_ip, get_admin_user
from app.schemas.admin.catalog import BrandWrite
from app.services.admin.catalog import BrandService

router = APIRouter(prefix="/brands", tags=["Admin Brands"])


@router.get("")
def list_brands(q: str | None = None, user: dict = Depends(get_admin_user)):
    return BrandService().list(q)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_brand(payload: BrandWrite, request: Request, user: dict = Depends(get_admin_user)):
    return BrandService().create(payload, user, client_ip(request))


@router.put("/{brand_id}")
def update_brand(
    brand_id: str, payload: BrandWrite, request: Request, user: dict = Depends(get_admin_user)
):
    return BrandService().update(brand_id, payload, user, client_ip(request))


@router.delete("/{brand_id}")
def delete_brand(brand_id: str, request: Request, user: dict = Depends(get_admin_user)):
    return BrandService().delete(brand_id, user, client_ip(request))
