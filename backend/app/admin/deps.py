from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.admin.templating import templates
from app.core.admin_auth import admin_from_cookie, new_csrf_token
from app.core.config import settings


def admin_required(request: Request) -> dict:
    admin = admin_from_cookie(request)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": f"/admin/login?next={request.url.path}"},
        )
    request.state.admin = admin
    return admin


def render(request: Request, name: str, ctx: Optional[dict] = None, status_code: int = 200) -> HTMLResponse:
    """Render an Option A template with a CSRF token consistent with the double-submit cookie.

    The form token always equals the ``admin_csrf`` cookie: the cookie is read from the
    request when present, otherwise a new token is generated and set on the response.
    """
    token = request.cookies.get(settings.ADMIN_CSRF_COOKIE)
    set_cookie = token is None
    if token is None:
        token = new_csrf_token()
    context = {
        "request": request,
        "admin": getattr(request.state, "admin", None),
        "csrf_token": token,
    }
    if ctx:
        context.update(ctx)
    response = templates.TemplateResponse(request, name, context, status_code=status_code)
    if set_cookie:
        response.set_cookie(
            key=settings.ADMIN_CSRF_COOKIE,
            value=token,
            httponly=True,
            samesite="lax",
            secure=settings.ADMIN_COOKIE_SECURE,
            path="/admin",
        )
    return response
