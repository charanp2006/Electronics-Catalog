from fastapi import APIRouter

from app.api.v1.admin import auth, brands, categories, orders, products, reviews, stats

router = APIRouter(prefix="/admin")
router.include_router(auth.router)
router.include_router(stats.router)
router.include_router(products.router)
router.include_router(categories.router)
router.include_router(brands.router)
router.include_router(orders.router)
router.include_router(reviews.router)
