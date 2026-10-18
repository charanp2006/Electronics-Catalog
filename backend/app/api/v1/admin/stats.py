from fastapi import APIRouter, Depends

from app.core.admin_auth import get_admin_user
from app.services.admin.stats import StatsService

router = APIRouter(prefix="/stats", tags=["Admin Stats"])


@router.get("")
def overview(user: dict = Depends(get_admin_user)):
    return StatsService().overview()
