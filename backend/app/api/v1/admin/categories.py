from fastapi import APIRouter, Depends, Request, status

from app.core.admin_auth import client_ip, get_admin_user
from app.schemas.admin.catalog import CategoryWrite
from app.services.admin.catalog import CategoryService

router = APIRouter(prefix="/categories", tags=["Admin Categories"])


@router.get("")
def list_categories(q: str | None = None, user: dict = Depends(get_admin_user)):
    return CategoryService().list(q)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryWrite, request: Request, user: dict = Depends(get_admin_user)):
    return CategoryService().create(payload, user, client_ip(request))


@router.put("/{category_id}")
def update_category(
    category_id: str, payload: CategoryWrite, request: Request, user: dict = Depends(get_admin_user)
):
    return CategoryService().update(category_id, payload, user, client_ip(request))


@router.delete("/{category_id}")
def delete_category(category_id: str, request: Request, user: dict = Depends(get_admin_user)):
    return CategoryService().delete(category_id, user, client_ip(request))
