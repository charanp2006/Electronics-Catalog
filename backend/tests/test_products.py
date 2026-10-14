API = "/api/v1"


def test_list_products(client):
    res = client.get(f"{API}/products/")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 12
    assert len(body["items"]) == 12
    assert {"_id", "name", "slug", "price"} <= set(body["items"][0])


def test_search_products(client):
    res = client.get(f"{API}/products/", params={"q": "apple"})
    names = " ".join(i["name"] for i in res.json()["items"])
    assert "Apple" in names


def test_filter_by_category(client):
    res = client.get(f"{API}/products/", params={"category": "laptops"})
    items = res.json()["items"]
    assert len(items) >= 1
    assert all(i["category"]["slug"] == "laptops" for i in items)


def test_filter_by_brand(client):
    res = client.get(f"{API}/products/", params={"brand": "sony"})
    assert all(i["brand"]["slug"] == "sony" for i in res.json()["items"])


def test_price_range_filter(client):
    res = client.get(f"{API}/products/", params={"min_price": 20000, "max_price": 40000})
    for item in res.json()["items"]:
        price = item["discount_price"] or item["price"]
        assert 20000 <= price <= 40000


def test_sort_price_asc(client):
    res = client.get(f"{API}/products/", params={"sort": "price_asc"})
    prices = [(i["discount_price"] or i["price"]) for i in res.json()["items"]]
    assert prices == sorted(prices)


def test_pagination(client):
    page1 = client.get(f"{API}/products/", params={"page": 1, "limit": 5}).json()
    page2 = client.get(f"{API}/products/", params={"page": 2, "limit": 5}).json()
    assert len(page1["items"]) == 5
    assert page1["items"][0]["_id"] != page2["items"][0]["_id"]


def test_product_detail(client):
    res = client.get(f"{API}/products/samsung-galaxy-s24")
    assert res.status_code == 200
    body = res.json()
    assert body["slug"] == "samsung-galaxy-s24"
    assert body["specifications"]
    assert "reviews" in body


def test_product_detail_not_found(client):
    assert client.get(f"{API}/products/does-not-exist").status_code == 404


def test_featured_and_related(client):
    assert len(client.get(f"{API}/products/featured").json()) >= 1
    related = client.get(f"{API}/products/samsung-galaxy-s24/related").json()
    assert all(p["slug"] != "samsung-galaxy-s24" for p in related)


def test_categories_and_brands(client):
    cats = client.get(f"{API}/categories/").json()
    brands = client.get(f"{API}/brands/").json()
    assert len(cats) == 4
    assert len(brands) == 8
    assert cats[0]["product_count"] >= 0
