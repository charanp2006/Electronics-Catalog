"""Admin authentication & authorization helpers.

Shared by the JSON API (Option B) and the server-rendered pages (Option A).
The single source of truth for "is this user an admin?" is ``users.is_admin``.
"""
from __future__ import annotations

import secrets
import time
from typing import Optional

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.security import create_access_token, decode_token, get_current_user, public_user
from app.db.mongodb import get_db

# ---------------------------------------------------------------------------
# Rate limiting (in-process; fine for a single instance)
# ---------------------------------------------------------------------------
_ATTEMPTS: dict[str, list[float]] = {}


def _prune(key: str) -> list[float]:
    window = settings.ADMIN_LOGIN_RATE_WINDOW_MINUTES * 60
    now = time.monotonic()
    kept = [t for t in _ATTEMPTS.get(key, []) if now - t < window]
    _ATTEMPTS[key] = kept
    return kept


def client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


def login_rate_key(request: Request, email: str) -> str:
    return f"{client_ip(request) or 'unknown'}:{email.lower()}"


def enforce_login_rate(key: str) -> None:
    if len(_prune(key)) >= settings.ADMIN_LOGIN_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )


def record_login_failure(key: str) -> None:
    _ATTEMPTS.setdefault(key, []).append(time.monotonic())


def clear_login_attempts(key: str) -> None:
    _ATTEMPTS.pop(key, None)


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------
def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    """Require an authenticated *administrator* (bearer token)."""
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
    return user


def issue_admin_token(user_id: str) -> str:
    return create_access_token(subject=str(user_id), scope="admin")


# ---------------------------------------------------------------------------
# Option A — cookie session
# ---------------------------------------------------------------------------
def set_admin_session(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.ADMIN_SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.ADMIN_COOKIE_SECURE,
        path="/admin",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def clear_admin_session(response: Response) -> None:
    response.delete_cookie(key=settings.ADMIN_SESSION_COOKIE, path="/admin")


def admin_from_cookie(request: Request) -> Optional[dict]:
    token = request.cookies.get(settings.ADMIN_SESSION_COOKIE)
    if not token:
        return None
    try:
        payload = decode_token(token)
    except Exception:
        return None
    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        return None
    user = get_db()["users"].find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("is_admin"):
        return None
    return public_user(user)


# ---------------------------------------------------------------------------
# Option A — CSRF (double submit cookie)
# ---------------------------------------------------------------------------
def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def verify_csrf(form_token: Optional[str], cookie_token: Optional[str]) -> bool:
    if not form_token or not cookie_token:
        return False
    return secrets.compare_digest(form_token, cookie_token)
