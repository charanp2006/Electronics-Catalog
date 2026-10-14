from fastapi import APIRouter

from app.repositories.category import CategoryRepository

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
def list_categories():
    return CategoryRepository().list_all()
