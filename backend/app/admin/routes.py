from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.admin.deps import admin_required, render
from app.core.admin_auth import (
    clear_admin_session,
    clear_login_attempts,
    enforce_login_rate,
    issue_admin_token,
    login_rate_key,
    new_csrf_token,
    record_login_failure,
    set_admin_session,
    verify_csrf,
)
from app.core.config import settings
from app.core.security import verify_password
from app.repositories.user import UserRepository
from app.schemas.admin.catalog import BrandWrite, CategoryWrite
from app.schemas.admin.product import ProductWrite
from app.schemas.admin.review import ReviewUpdate
from app.services.admin.catalog import BrandService, CategoryService
from app.services.admin.orders import ALLOWED_TRANSITIONS, OrderService
from app.services.admin.products import ProductService
from app.services.admin.reviews import ReviewService
from app.services.admin.stats import StatsService

router = APIRouter(include_in_schema=False)


def _safe_next(url: Optional[str]) -> str:
    """Only allow post-login redirects back into the admin area."""
    if url and url.startswith("/admin"):
        return url
    return "/admin"


def _detail(e: HTTPException) -> str:
    return e.detail if isinstance(e.detail, str) else "Request failed"


def _require_csrf(csrf_token: Optional[str], csrf_cookie: Optional[str]) -> None:
    if not verify_csrf(csrf_token, csrf_cookie):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: Optional[str] = None):
    return render(request, "admin/login.html", {"error": error})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
):
    if not verify_csrf(csrf_token, csrf_cookie):
        return render(request, "admin/login.html", {"error": "Invalid CSRF token — please retry."}, status_code=400)
    key = login_rate_key(request, email)
    enforce_login_rate(key)
    user = UserRepository().get_by_email(email)
    if not user or not user.get("is_admin") or not verify_password(password, user.get("password", "")):
        record_login_failure(key)
        return render(request, "admin/login.html", {"error": "Invalid credentials"}, status_code=401)
    clear_login_attempts(key)
    token = issue_admin_token(str(user["_id"]))
    request.state.admin = user
    resp = RedirectResponse(url=_safe_next(request.query_params.get("next")), status_code=303)
    set_admin_session(resp, token)
    resp.set_cookie(
        key=settings.ADMIN_CSRF_COOKIE,
        value=new_csrf_token(),
        httponly=True,
        samesite="lax",
        secure=settings.ADMIN_COOKIE_SECURE,
        path="/admin",
    )
    return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/admin/login?msg=logged_out", status_code=303)
    clear_admin_session(resp)
    return resp


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, admin: dict = Depends(admin_required)):
    stats = StatsService().overview()
    return render(request, "admin/dashboard.html", {"stats": stats})


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
def _product_form_values(name="", slug="", brand="", category="", price="", discount_price="",
                         stock=0, images=None, is_active=True, is_featured=False):
    return {
        "name": name,
        "slug": slug,
        "brand": {"slug": brand} if isinstance(brand, str) else brand,
        "category": {"slug": category} if isinstance(category, str) else category,
        "price": price,
        "discount_price": discount_price,
        "stock": stock,
        "images": images or [],
        "is_active": is_active,
        "is_featured": is_featured,
    }


@router.get("/products", response_class=HTMLResponse)
def products_list(request: Request, admin: dict = Depends(admin_required), page: int = Query(1)):
    data = ProductService().list(page=page, limit=50)
    return render(request, "admin/products/list.html", {"products": data})


@router.get("/products/new", response_class=HTMLResponse)
def products_new(request: Request, admin: dict = Depends(admin_required)):
    return render(request, "admin/products/form.html", {"product": None})


@router.post("/products/new")
def products_create(
    request: Request,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    name: str = Form(...),
    slug: str = Form(""),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    discount_price: Optional[float] = Form(None),
    stock: int = Form(0),
    image_urls: str = Form(""),
    is_active: Optional[str] = Form(None),
    is_featured: Optional[str] = Form(None),
):
    _require_csrf(csrf_token, csrf_cookie)
    form_values = _product_form_values(
        name=name, slug=slug, brand=brand, category=category, price=price,
        discount_price=discount_price, stock=stock,
        images=[u.strip() for u in image_urls.split(",") if u.strip()],
        is_active=bool(is_active), is_featured=bool(is_featured),
    )
    payload = ProductWrite(
        name=name,
        slug=slug or None,
        brand=brand,
        category=category,
        price=price,
        discount_price=discount_price,
        stock=stock,
        image_urls=image_urls or None,
        is_active=bool(is_active),
        is_featured=bool(is_featured),
    )
    try:
        ProductService().create(payload, admin)
    except HTTPException as e:
        return render(request, "admin/products/form.html",
                      {"product": form_values, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/products?msg=created", status_code=303)


@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
def products_edit(request: Request, product_id: str, admin: dict = Depends(admin_required)):
    product = ProductService().get(product_id)
    return render(request, "admin/products/form.html", {"product": product, "is_edit": True})


@router.post("/products/{product_id}/edit")
def products_update(
    request: Request,
    product_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    name: str = Form(...),
    slug: str = Form(""),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    discount_price: Optional[float] = Form(None),
    stock: int = Form(0),
    image_urls: str = Form(""),
    is_active: Optional[str] = Form(None),
    is_featured: Optional[str] = Form(None),
):
    _require_csrf(csrf_token, csrf_cookie)
    form_values = _product_form_values(
        name=name, slug=slug, brand=brand, category=category, price=price,
        discount_price=discount_price, stock=stock,
        images=[u.strip() for u in image_urls.split(",") if u.strip()],
        is_active=bool(is_active), is_featured=bool(is_featured),
    )
    payload = ProductWrite(
        name=name,
        slug=slug or None,
        brand=brand,
        category=category,
        price=price,
        discount_price=discount_price,
        stock=stock,
        image_urls=image_urls or None,
        is_active=bool(is_active),
        is_featured=bool(is_featured),
    )
    try:
        ProductService().update(product_id, payload, admin)
    except HTTPException as e:
        return render(request, "admin/products/form.html",
                      {"product": form_values, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/products?msg=updated", status_code=303)


@router.post("/products/{product_id}/delete")
def products_delete(
    request: Request,
    product_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
):
    _require_csrf(csrf_token, csrf_cookie)
    ProductService().delete(product_id, admin)
    return RedirectResponse(url="/admin/products?msg=deleted", status_code=303)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
@router.get("/categories", response_class=HTMLResponse)
def categories_list(request: Request, admin: dict = Depends(admin_required), edit: Optional[str] = None):
    categories = CategoryService().list()
    edit_cat = None
    if edit:
        try:
            edit_cat = CategoryService().get(edit)
        except HTTPException:
            edit_cat = None
    return render(request, "admin/categories/list.html", {"categories": categories, "edit": edit_cat})


@router.post("/categories/new")
def categories_create(
    request: Request,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    name: str = Form(...),
    slug: str = Form(""),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        CategoryService().create(CategoryWrite(name=name, slug=slug or None), admin)
    except HTTPException as e:
        categories = CategoryService().list()
        return render(request, "admin/categories/list.html",
                      {"categories": categories, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/categories?msg=created", status_code=303)


@router.post("/categories/{category_id}/edit")
def categories_update(
    request: Request,
    category_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    name: str = Form(...),
    slug: str = Form(""),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        CategoryService().update(category_id, CategoryWrite(name=name, slug=slug or None), admin)
    except HTTPException as e:
        categories = CategoryService().list()
        return render(request, "admin/categories/list.html",
                      {"categories": categories, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/categories?msg=updated", status_code=303)


@router.post("/categories/{category_id}/delete")
def categories_delete(
    request: Request,
    category_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        CategoryService().delete(category_id, admin)
    except HTTPException as e:
        categories = CategoryService().list()
        return render(request, "admin/categories/list.html",
                      {"categories": categories, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/categories?msg=deleted", status_code=303)


# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------
@router.get("/brands", response_class=HTMLResponse)
def brands_list(request: Request, admin: dict = Depends(admin_required), edit: Optional[str] = None):
    brands = BrandService().list()
    edit_brand = None
    if edit:
        try:
            doc = BrandService().repo.get_by_id(edit)
            edit_brand = doc
        except Exception:
            edit_brand = None
    return render(request, "admin/brands/list.html", {"brands": brands, "edit": edit_brand})


@router.post("/brands/new")
def brands_create(
    request: Request,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    name: str = Form(...),
    slug: str = Form(""),
    country: str = Form(""),
    logo: str = Form(""),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        BrandService().create(
            BrandWrite(name=name, slug=slug or None, country=country or None, logo=logo or None), admin
        )
    except HTTPException as e:
        brands = BrandService().list()
        return render(request, "admin/brands/list.html",
                      {"brands": brands, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/brands?msg=created", status_code=303)


@router.post("/brands/{brand_id}/edit")
def brands_update(
    request: Request,
    brand_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    name: str = Form(...),
    slug: str = Form(""),
    country: str = Form(""),
    logo: str = Form(""),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        BrandService().update(
            brand_id, BrandWrite(name=name, slug=slug or None, country=country or None, logo=logo or None), admin
        )
    except HTTPException as e:
        brands = BrandService().list()
        return render(request, "admin/brands/list.html",
                      {"brands": brands, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/brands?msg=updated", status_code=303)


@router.post("/brands/{brand_id}/delete")
def brands_delete(
    request: Request,
    brand_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        BrandService().delete(brand_id, admin)
    except HTTPException as e:
        brands = BrandService().list()
        return render(request, "admin/brands/list.html",
                      {"brands": brands, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/brands?msg=deleted", status_code=303)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
@router.get("/orders", response_class=HTMLResponse)
def orders_list(request: Request, admin: dict = Depends(admin_required), page: int = Query(1)):
    orders = OrderService().list(page=page, limit=50)
    return render(request, "admin/orders/list.html", {"orders": orders})


def _order_detail_ctx(order: dict, error: Optional[str] = None) -> dict:
    return {
        "order": order,
        "error": error,
        "allowed": sorted(ALLOWED_TRANSITIONS.get(order.get("status", "pending"), set())),
    }


@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail(request: Request, order_id: str, admin: dict = Depends(admin_required)):
    order = OrderService().get(order_id)
    return render(request, "admin/orders/detail.html", _order_detail_ctx(order))


@router.post("/orders/{order_id}/status")
def order_status(
    request: Request,
    order_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
    status_value: str = Form(..., alias="status"),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        OrderService().set_status(order_id, status_value, admin)
    except HTTPException as e:
        order = OrderService().get(order_id)
        return render(request, "admin/orders/detail.html",
                      _order_detail_ctx(order, error=_detail(e)), status_code=e.status_code)
    return RedirectResponse(url=f"/admin/orders/{order_id}?msg=updated", status_code=303)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
@router.get("/reviews", response_class=HTMLResponse)
def reviews_list(request: Request, admin: dict = Depends(admin_required), page: int = Query(1)):
    reviews = ReviewService().list(page=page, limit=50)
    return render(request, "admin/reviews/list.html", {"reviews": reviews})


@router.post("/reviews/{product_id}/{review_id}/toggle")
def review_toggle(
    request: Request,
    product_id: str,
    review_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
):
    _require_csrf(csrf_token, csrf_cookie)
    service = ReviewService()
    try:
        _raw, _reviews, review = service._find(product_id, review_id)
    except HTTPException as e:
        reviews = service.list(page=1, limit=50)
        return render(request, "admin/reviews/list.html",
                      {"reviews": reviews, "error": _detail(e)}, status_code=e.status_code)
    new_status = "hidden" if review.get("status") == "published" else "published"
    service.moderate(product_id, review_id, ReviewUpdate(status=new_status), admin)
    return RedirectResponse(url="/admin/reviews?msg=updated", status_code=303)


@router.post("/reviews/{product_id}/{review_id}/delete")
def review_delete(
    request: Request,
    product_id: str,
    review_id: str,
    admin: dict = Depends(admin_required),
    csrf_token: Optional[str] = Form(None),
    csrf_cookie: Optional[str] = Cookie(None, alias=settings.ADMIN_CSRF_COOKIE),
):
    _require_csrf(csrf_token, csrf_cookie)
    try:
        ReviewService().delete(product_id, review_id, admin)
    except HTTPException as e:
        reviews = ReviewService().list(page=1, limit=50)
        return render(request, "admin/reviews/list.html",
                      {"reviews": reviews, "error": _detail(e)}, status_code=e.status_code)
    return RedirectResponse(url="/admin/reviews?msg=deleted", status_code=303)
