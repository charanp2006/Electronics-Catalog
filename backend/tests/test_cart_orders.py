API = "/api/v1"


def test_cart_requires_auth(client):
    assert client.get(f"{API}/cart/").status_code == 401


def test_cart_crud(client, auth_headers, first_product):
    pid = first_product["_id"]

    add = client.post(f"{API}/cart/add", json={"product_id": pid, "quantity": 2}, headers=auth_headers)
    assert add.status_code == 200
    assert add.json()["count"] == 2

    cart = client.get(f"{API}/cart/", headers=auth_headers).json()
    assert cart["items"][0]["quantity"] == 2
    assert cart["total"] == (cart["items"][0]["discount_price"] or cart["items"][0]["price"]) * 2

    upd = client.put(f"{API}/cart/update", json={"product_id": pid, "quantity": 1}, headers=auth_headers)
    assert upd.json()["count"] == 1

    rem = client.delete(f"{API}/cart/remove/{pid}", headers=auth_headers)
    assert rem.json()["count"] == 0


def test_wishlist_toggle(client, auth_headers, first_product):
    pid = first_product["_id"]
    added = client.post(f"{API}/wishlist/add", json={"product_id": pid}, headers=auth_headers)
    assert len(added.json()) == 1
    removed = client.delete(f"{API}/wishlist/remove/{pid}", headers=auth_headers)
    assert len(removed.json()) == 0


def test_add_review_updates_rating(client, auth_headers):
    before = client.get(f"{API}/products/samsung-galaxy-s24").json()
    res = client.post(
        f"{API}/products/samsung-galaxy-s24/reviews",
        json={"rating": 4, "comment": "Solid device"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    after = res.json()
    assert after["total_reviews"] == before["total_reviews"] + 1


def test_review_validation(client, auth_headers):
    res = client.post(
        f"{API}/products/samsung-galaxy-s24/reviews",
        json={"rating": 9, "comment": "bad"},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_order_flow_decrements_stock(client, auth_headers, first_product):
    pid = first_product["_id"]
    slug = first_product["slug"]
    stock_before = client.get(f"{API}/products/{slug}").json()["stock"]

    client.post(f"{API}/cart/add", json={"product_id": pid, "quantity": 1}, headers=auth_headers)
    order = client.post(f"{API}/orders/", json={}, headers=auth_headers)
    assert order.status_code == 201
    assert order.json()["status"] == "placed"

    stock_after = client.get(f"{API}/products/{slug}").json()["stock"]
    assert stock_after == stock_before - 1
    assert client.get(f"{API}/cart/", headers=auth_headers).json()["count"] == 0
    assert len(client.get(f"{API}/orders/", headers=auth_headers).json()) >= 1


def test_order_empty_cart(client, auth_headers):
    client.delete(f"{API}/cart/clear", headers=auth_headers)
    res = client.post(f"{API}/orders/", json={}, headers=auth_headers)
    assert res.status_code == 400
