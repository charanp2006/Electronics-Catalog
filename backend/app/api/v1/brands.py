from fastapi import APIRouter

from app.repositories.brand import BrandRepository

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get("/")
def list_brands():
    return BrandRepository().list_all()
