from fastapi import APIRouter, Depends, Request

from app.core.admin_auth import client_ip, get_admin_user
from app.schemas.admin.review import ReviewUpdate
from app.services.admin.reviews import ReviewService

router = APIRouter(prefix="/reviews", tags=["Admin Reviews"])


@router.get("")
def list_reviews(
    product_id: str | None = None,
    status: str | None = None,
    rating: int | None = None,
    q: str | None = None,
    sort: str = "newest",
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(get_admin_user),
):
    return ReviewService().list(
        product_id=product_id, status=status, rating=rating, q=q, sort=sort, page=page, limit=limit
    )


@router.patch("/{product_id}/{review_id}")
def moderate_review(
    product_id: str,
    review_id: str,
    payload: ReviewUpdate,
    request: Request,
    user: dict = Depends(get_admin_user),
):
    return ReviewService().moderate(product_id, review_id, payload, user, client_ip(request))


@router.delete("/{product_id}/{review_id}")
def delete_review(
    product_id: str, review_id: str, request: Request, user: dict = Depends(get_admin_user)
):
    return ReviewService().delete(product_id, review_id, user, client_ip(request))
