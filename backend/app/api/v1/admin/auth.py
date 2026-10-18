from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.admin_auth import (
    clear_login_attempts,
    enforce_login_rate,
    get_admin_user,
    issue_admin_token,
    login_rate_key,
    record_login_failure,
)
from app.core.security import public_user, verify_password
from app.repositories.user import UserRepository
from app.schemas.admin.auth import AdminLoginRequest, AdminTokenResponse

router = APIRouter(prefix="/auth", tags=["Admin Auth"])


def _admin_out(user: dict) -> dict:
    return {
        "id": user["_id"],
        "name": user.get("name"),
        "username": user["username"],
        "email": user["email"],
        "is_admin": True,
    }


@router.post("/login", response_model=AdminTokenResponse)
def login(payload: AdminLoginRequest, request: Request):
    key = login_rate_key(request, payload.email)
    enforce_login_rate(key)

    user = UserRepository().get_by_email(payload.email)
    if (
        not user
        or not user.get("is_admin")
        or not verify_password(payload.password, user.get("password", ""))
    ):
        record_login_failure(key)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    clear_login_attempts(key)
    public = public_user(user)
    return {
        "access_token": issue_admin_token(public["_id"]),
        "token_type": "bearer",
        "admin": {
            "id": public["_id"],
            "name": public.get("name"),
            "username": public["username"],
            "email": public["email"],
            "is_admin": True,
        },
    }


@router.get("/me")
def me(user: dict = Depends(get_admin_user)):
    public = user
    return {
        "id": public["_id"],
        "name": public.get("name"),
        "username": public["username"],
        "email": public["email"],
        "is_admin": True,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    return Response(status_code=status.HTTP_204_NO_CONTENT)
