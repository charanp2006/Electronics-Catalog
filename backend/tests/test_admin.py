"""Admin API tests — authz matrix and core CRUD flows."""
API = "/api/v1"
ADMIN = f"{API}/admin"


def test_anonymous_is_unauthorized(client):
    assert client.get(f"{ADMIN}/products").status_code == 401
    assert client.get(f"{ADMIN}/stats").status_code == 401


def test_customer_is_forbidden(client, auth_headers):
    assert client.get(f"{ADMIN}/products", headers=auth_headers).status_code == 403


def test_customer_login_rejected_on_admin(client):
    res = client.post(
        f"{ADMIN}/auth/login",
        json={"email": "demo@example.com", "password": "demo12345"},
    )
    assert res.status_code == 401


def test_admin_login_and_me(client, admin_headers):
    res = client.get(f"{ADMIN}/auth/me", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["is_admin"] is True


def test_stats_overview(client, admin_headers):
    res = client.get(f"{ADMIN}/stats", headers=admin_headers)
    assert res.status_code == 200
    body = res.json()
    assert {"products", "orders", "reviews", "catalog", "recent_orders"} <= set(body)
    assert body["products"]["total"] >= 12
    assert "by_status" in body["orders"]


def test_category_crud(client, admin_headers):
    created = client.post(
        f"{ADMIN}/categories",
        json={"name": "Smart Wearables", "description": "Watches & bands"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    category = created.json()
    assert category["slug"] == "smart-wearables"

    updated = client.put(
        f"{ADMIN}/categories/{category['_id']}",
        json={"name": "Wearable Tech", "description": "Watches & bands"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["slug"] == "wearable-tech"

    deleted = client.delete(f"{ADMIN}/categories/{category['_id']}", headers=admin_headers)
    assert deleted.json() == {"deleted": True}


def test_category_delete_blocked_when_in_use(client, admin_headers):
    categories = client.get(f"{ADMIN}/categories", headers=admin_headers).json()
    smartphones = next(c for c in categories if c["slug"] == "smartphones")
    res = client.delete(f"{ADMIN}/categories/{smartphones['_id']}", headers=admin_headers)
    assert res.status_code == 409


def test_brand_crud(client, admin_headers):
    created = client.post(
        f"{ADMIN}/brands",
        json={"name": "Nothing", "country": "UK", "logo": "https://picsum.photos/seed/nb/120/60"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    brand = created.json()
    assert brand["slug"] == "nothing"

    updated = client.put(
        f"{ADMIN}/brands/{brand['_id']}",
        json={"name": "Nothing Tech", "country": "UK"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["slug"] == "nothing-tech"

    deleted = client.delete(f"{ADMIN}/brands/{brand['_id']}", headers=admin_headers)
    assert deleted.json() == {"deleted": True}


def test_product_crud_and_images(client, admin_headers):
    payload = {
        "name": "Test Widget X",
        "brand": "apple",
        "category": "smartphones",
        "price": 1000,
        "discount_price": 900,
        "stock": 3,
        "image_urls": "https://picsum.photos/seed/w1/600/600, https://picsum.photos/seed/w2/600/600",
        "specifications": [{"key": "Color", "value": "Black"}],
    }
    created = client.post(f"{ADMIN}/products", json=payload, headers=admin_headers)
    assert created.status_code == 201, created.text
    product = created.json()
    assert product["slug"] == "test-widget-x"
    assert product["image"] == "https://picsum.photos/seed/w1/600/600"
    assert len(product["images"]) == 2

    pid = product["_id"]
    patched = client.patch(f"{ADMIN}/products/{pid}", json={"stock": 1}, headers=admin_headers)
    assert patched.status_code == 200
    assert patched.json()["stock"] == 1
    assert patched.json()["price"] == 1000

    soft = client.delete(f"{ADMIN}/products/{pid}", headers=admin_headers)
    assert soft.json() == {"deleted": True, "hard": False}
    assert client.get(f"{ADMIN}/products/{pid}", headers=admin_headers).json()["is_active"] is False

    hard = client.delete(f"{ADMIN}/products/{pid}?hard=true", headers=admin_headers)
    assert hard.json()["hard"] is True
    assert client.get(f"{ADMIN}/products/{pid}", headers=admin_headers).status_code == 404


def test_product_invalid_image_url(client, admin_headers):
    payload = {
        "name": "Bad Image",
        "brand": "apple",
        "category": "smartphones",
        "price": 10,
        "image_urls": "not-a-url",
    }
    res = client.post(f"{ADMIN}/products", json=payload, headers=admin_headers)
    assert res.status_code == 400


def test_product_discount_validation(client, admin_headers):
    payload = {
        "name": "Bad Discount",
        "brand": "apple",
        "category": "smartphones",
        "price": 100,
        "discount_price": 200,
    }
    res = client.post(f"{ADMIN}/products", json=payload, headers=admin_headers)
    assert res.status_code == 422


def test_order_status_transitions(client, admin_headers):
    orders = client.get(f"{ADMIN}/orders", headers=admin_headers).json()["items"]
    pending = next(o for o in orders if o["status"] == "pending")

    bad = client.patch(
        f"{ADMIN}/orders/{pending['id']}/status", json={"status": "delivered"}, headers=admin_headers
    )
    assert bad.status_code == 400

    ok = client.patch(
        f"{ADMIN}/orders/{pending['id']}/status", json={"status": "processing"}, headers=admin_headers
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "processing"
    assert ok.json()["status_history"][-1]["status"] == "processing"


def test_review_moderation_recomputes_rating(client, admin_headers):
    product = client.get(f"{API}/products/samsung-galaxy-s24").json()
    reviews = client.get(
        f"{ADMIN}/reviews", params={"product_id": product["_id"]}, headers=admin_headers
    ).json()
    assert reviews["total"] >= 1
    target = reviews["items"][0]

    res = client.patch(
        f"{ADMIN}/reviews/{target['product_id']}/{target['review_id']}",
        json={"status": "hidden"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "hidden"

    after = client.get(f"{API}/products/samsung-galaxy-s24").json()
    assert after["total_reviews"] < product["total_reviews"]
