"""Option A (server-rendered /admin) tests — auth redirect, cookie session, CSRF, flows."""
import re

from conftest import ADMIN_EMAIL, ADMIN_PASSWORD
from app.core.admin_auth import issue_admin_token
from app.db.mongodb import get_db
from app.repositories.user import UserRepository

API = "/api/v1"
ADMIN = "/admin"
CREDS = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}


def _extract_csrf(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, "csrf_token hidden field missing"
    return m.group(1)


def _csrf(client) -> str:
    res = client.get(f"{ADMIN}/login")
    assert res.status_code == 200
    token = _extract_csrf(res.text)
    assert client.cookies.get("admin_csrf") == token, "form token must match csrf cookie"
    return token


def _login(client) -> None:
    token = _csrf(client)
    res = client.post(f"{ADMIN}/login", data={**CREDS, "csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303, res.text
    assert res.headers["location"].startswith("/admin")
    assert client.cookies.get("admin_session"), "admin_session cookie not set"


# ---------------------------------------------------------------------------
# Phase 5 — security headers + route surface
# ---------------------------------------------------------------------------
def test_security_headers_present(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"
    assert res.headers["referrer-policy"] == "same-origin"


def test_option_a_not_exposed_at_root(client):
    for path in ("/login", "/products", "/categories", "/brands", "/orders", "/reviews"):
        assert client.get(path).status_code == 404, path


def test_static_css_served(client):
    res = client.get(f"{ADMIN}/static/admin.css")
    assert res.status_code == 200
    assert "text/css" in res.headers["content-type"]


# ---------------------------------------------------------------------------
# Auth matrix
# ---------------------------------------------------------------------------
def test_anonymous_redirected_to_login(client):
    for path in ("/admin", "/admin/products", "/admin/orders", "/admin/reviews"):
        res = client.get(path, follow_redirects=False)
        assert res.status_code == 303, path
        assert res.headers["location"].startswith("/admin/login"), path


def test_login_page_sets_consistent_csrf(client):
    _csrf(client)


def test_login_rejects_missing_csrf(client):
    _csrf(client)
    res = client.post(f"{ADMIN}/login", data={**CREDS, "csrf_token": "forged"}, follow_redirects=False)
    assert res.status_code == 400


def test_login_rejects_bad_credentials(client):
    token = _csrf(client)
    res = client.post(
        f"{ADMIN}/login",
        data={"email": "nobody-nowhere@example.com", "password": "nope", "csrf_token": token},
        follow_redirects=False,
    )
    assert res.status_code == 401


def test_login_rejects_non_admin(client):
    token = _csrf(client)
    res = client.post(
        f"{ADMIN}/login",
        data={"email": "demo@example.com", "password": "demo12345", "csrf_token": token},
        follow_redirects=False,
    )
    assert res.status_code == 401


def test_login_success_and_dashboard(client):
    _login(client)
    res = client.get(f"{ADMIN}/")
    assert res.status_code == 200
    assert "Dashboard" in res.text
    assert client.cookies.get("admin_session"), "admin_session cookie missing after login"


def test_non_admin_session_cookie_rejected(client):
    demo = UserRepository().get_by_email("demo@example.com")
    assert demo, "demo user missing — did seed run?"
    client.cookies.set("admin_session", issue_admin_token(str(demo["_id"])))
    res = client.get(f"{ADMIN}/", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"].startswith("/admin/login")


def test_logout_clears_session(client):
    _login(client)
    res = client.get(f"{ADMIN}/logout", follow_redirects=False)
    assert res.status_code == 303
    assert client.cookies.get("admin_session") in (None, "")
    res = client.get(f"{ADMIN}/", follow_redirects=False)
    assert res.status_code == 303


# ---------------------------------------------------------------------------
# Products via server-rendered forms
# ---------------------------------------------------------------------------
def test_product_create_edit_delete_roundtrip(client):
    _login(client)

    page = client.get(f"{ADMIN}/products/new")
    assert page.status_code == 200
    token = _extract_csrf(page.text)

    res = client.post(
        f"{ADMIN}/products/new",
        data={
            "csrf_token": token,
            "name": "Option A Gadget",
            "slug": "",
            "brand": "apple",
            "category": "smartphones",
            "price": "4999",
            "discount_price": "4499",
            "stock": "5",
            "image_urls": "https://picsum.photos/seed/oa1/600/600, https://picsum.photos/seed/oa2/600/600",
            "is_active": "on",
        },
        follow_redirects=False,
    )
    assert res.status_code == 303
    listed = client.get(f"{ADMIN}/products")
    assert "Option A Gadget" in listed.text

    from app.repositories.product import ProductRepository

    doc = ProductRepository().collection.find_one({"slug": "option-a-gadget"})
    assert doc and doc["image"] == "https://picsum.photos/seed/oa1/600/600"
    assert len(doc["images"]) == 2
    pid = str(doc["_id"])

    form = client.get(f"{ADMIN}/products/{pid}/edit")
    assert form.status_code == 200
    token = _extract_csrf(form.text)
    res = client.post(
        f"{ADMIN}/products/{pid}/edit",
        data={
            "csrf_token": token,
            "name": "Option A Gadget v2",
            "slug": "option-a-gadget",
            "brand": "apple",
            "category": "smartphones",
            "price": "5999",
            "discount_price": "",
            "stock": "9",
            "image_urls": "https://picsum.photos/seed/oa1/600/600",
            "is_active": "on",
            "is_featured": "on",
        },
        follow_redirects=False,
    )
    assert res.status_code == 303
    updated = ProductRepository().collection.find_one({"_id": doc["_id"]})
    assert updated["name"] == "Option A Gadget v2"
    assert updated["is_featured"] is True
    assert updated["price_history"], "price change must append price_history"

    token = _extract_csrf(client.get(f"{ADMIN}/products").text)
    res = client.post(f"{ADMIN}/products/{pid}/delete", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303
    assert ProductRepository().collection.find_one({"_id": doc["_id"]})["is_active"] is False


def test_product_create_requires_csrf(client):
    _login(client)
    res = client.post(
        f"{ADMIN}/products/new",
        data={
            "csrf_token": "forged",
            "name": "No CSRF",
            "brand": "apple",
            "category": "smartphones",
            "price": "10",
            "stock": "1",
        },
        follow_redirects=False,
    )
    assert res.status_code == 400


def test_product_create_unknown_brand_rerenders_error(client):
    _login(client)
    page = client.get(f"{ADMIN}/products/new")
    token = _extract_csrf(page.text)
    res = client.post(
        f"{ADMIN}/products/new",
        data={
            "csrf_token": token,
            "name": "Orphan Product",
            "brand": "no-such-brand",
            "category": "smartphones",
            "price": "10",
            "stock": "1",
        },
        follow_redirects=False,
    )
    assert res.status_code == 400
    assert "Orphan Product" in res.text, "form should refill submitted values"
    assert 'class="alert"' in res.text, "validation error banner missing"
    assert "not found" in res.text.lower()


# ---------------------------------------------------------------------------
# Categories & brands via server-rendered forms
# ---------------------------------------------------------------------------
def _cat_id(client, slug):
    from app.repositories.category import CategoryRepository

    return str(CategoryRepository().get_by_slug(slug)["_id"])


def _brand_id(client, slug):
    from app.repositories.brand import BrandRepository

    return str(BrandRepository().get_by_slug(slug)["_id"])


def test_category_create_edit_delete(client):
    _login(client)
    token = _extract_csrf(client.get(f"{ADMIN}/categories").text)

    res = client.post(
        f"{ADMIN}/categories/new",
        data={"csrf_token": token, "name": "Gaming Monitors", "slug": ""},
        follow_redirects=False,
    )
    assert res.status_code == 303
    cid = _cat_id(client, "gaming-monitors")

    res = client.post(
        f"{ADMIN}/categories/{cid}/edit",
        data={"csrf_token": token, "name": "Gaming Displays", "slug": "gaming-monitors"},
        follow_redirects=False,
    )
    assert res.status_code == 303
    from app.repositories.category import CategoryRepository

    assert CategoryRepository().get_by_id(cid)["name"] == "Gaming Displays"

    res = client.post(f"{ADMIN}/categories/{cid}/delete", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303
    assert CategoryRepository().get_by_id(cid) is None


def test_category_delete_blocked_when_in_use(client):
    _login(client)
    cid = _cat_id(client, "smartphones")
    token = _extract_csrf(client.get(f"{ADMIN}/categories").text)
    res = client.post(f"{ADMIN}/categories/{cid}/delete", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 409
    assert "reference" in res.text.lower() or "cannot delete" in res.text.lower()


def test_brand_create_edit_delete(client):
    _login(client)
    token = _extract_csrf(client.get(f"{ADMIN}/brands").text)

    res = client.post(
        f"{ADMIN}/brands/new",
        data={"csrf_token": token, "name": "Framework", "slug": "", "country": "US", "logo": ""},
        follow_redirects=False,
    )
    assert res.status_code == 303
    bid = _brand_id(client, "framework")

    res = client.post(
        f"{ADMIN}/brands/{bid}/edit",
        data={"csrf_token": token, "name": "Framework Computer", "slug": "framework", "country": "USA", "logo": ""},
        follow_redirects=False,
    )
    assert res.status_code == 303
    from app.repositories.brand import BrandRepository

    assert BrandRepository().get_by_id(bid)["country"] == "USA"

    res = client.post(f"{ADMIN}/brands/{bid}/delete", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303
    assert BrandRepository().get_by_id(bid) is None


# ---------------------------------------------------------------------------
# Orders via server-rendered pages
# ---------------------------------------------------------------------------
def test_order_detail_shows_only_allowed_transitions(client):
    _login(client)
    db = get_db()
    order = db["orders"].find_one({"status": {"$in": ["pending", "processing", "shipped"]}})
    assert order, "seed must include an order with available transitions"
    from app.services.admin.orders import ALLOWED_TRANSITIONS

    current = order["status"]
    allowed = ALLOWED_TRANSITIONS[current]
    res = client.get(f"{ADMIN}/orders/{order['_id']}")
    assert res.status_code == 200
    for s in allowed:
        assert f'value="{s}"' in res.text, f"allowed transition {s} not offered"
    for s in set(ALLOWED_TRANSITIONS) - allowed - {current}:
        assert f'value="{s}"' not in res.text, f"illegal transition {s} must not be offered"


def test_order_status_update_and_illegal_transition(client):
    _login(client)
    db = get_db()
    order = db["orders"].find_one({"status": {"$in": ["pending", "processing", "shipped"]}})
    assert order, "seed must include an order with available transitions"
    from app.services.admin.orders import ALLOWED_TRANSITIONS

    current = order["status"]
    legal = sorted(ALLOWED_TRANSITIONS[current])[0]
    illegal = sorted(set(ALLOWED_TRANSITIONS) - ALLOWED_TRANSITIONS[current] - {current})[0]
    oid = str(order["_id"])
    token = _extract_csrf(client.get(f"{ADMIN}/orders/{oid}").text)

    res = client.post(
        f"{ADMIN}/orders/{oid}/status",
        data={"csrf_token": token, "status": illegal},
        follow_redirects=False,
    )
    assert res.status_code == 400
    assert "invalid status transition" in res.text.lower()

    res = client.post(
        f"{ADMIN}/orders/{oid}/status",
        data={"csrf_token": token, "status": legal},
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert db["orders"].find_one({"_id": order["_id"]})["status"] == legal


# ---------------------------------------------------------------------------
# Reviews moderation via server-rendered pages
# ---------------------------------------------------------------------------
def test_review_toggle_and_delete(client):
    _login(client)
    from app.repositories.product import ProductRepository

    repo = ProductRepository()
    product = repo.collection.find_one({"reviews.0": {"$exists": True}})
    assert product, "seed must include a product with reviews"
    review = product["reviews"][0]
    pid, rid = str(product["_id"]), review["review_id"]
    original_status = review.get("status", "published")
    flipped = "hidden" if original_status == "published" else "published"

    token = _extract_csrf(client.get(f"{ADMIN}/reviews").text)
    res = client.post(f"{ADMIN}/reviews/{pid}/{rid}/toggle", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303
    stored = repo.collection.find_one({"_id": product["_id"]})
    toggled = next(r for r in stored["reviews"] if r["review_id"] == rid)
    assert toggled["status"] == flipped

    # flip back so the delete step targets a known state
    res = client.post(f"{ADMIN}/reviews/{pid}/{rid}/toggle", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303

    res = client.post(f"{ADMIN}/reviews/{pid}/{rid}/delete", data={"csrf_token": token}, follow_redirects=False)
    assert res.status_code == 303
    stored = repo.collection.find_one({"_id": product["_id"]})
    assert all(r["review_id"] != rid for r in stored["reviews"])
