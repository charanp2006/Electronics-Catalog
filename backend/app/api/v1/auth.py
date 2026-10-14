from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    public_user,
    verify_password,
)
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])


def _token_response(user: dict) -> dict:
    public = public_user(user)
    return {
        "access_token": create_access_token(str(public["_id"])),
        "token_type": "bearer",
        "user": {
            "id": public["_id"],
            "name": public.get("name"),
            "username": public["username"],
            "email": public["email"],
        },
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    repo = UserRepository()
    if repo.get_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if repo.get_by_username(payload.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    doc = {
        "name": payload.name or payload.username,
        "username": payload.username,
        "email": payload.email.lower(),
        "password": hash_password(payload.password),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = repo.create(doc)
    doc["_id"] = result.inserted_id
    return _token_response(doc)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = UserRepository().get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(user)


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return {
        "id": user["_id"],
        "name": user.get("name"),
        "username": user["username"],
        "email": user["email"],
    }
