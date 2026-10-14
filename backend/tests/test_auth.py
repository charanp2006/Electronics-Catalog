API = "/api/v1"


def test_login_success(client):
    res = client.post(f"{API}/auth/login", json={"email": "demo@example.com", "password": "demo12345"})
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"]
    assert body["user"]["username"] == "demo"


def test_login_failure(client):
    res = client.post(f"{API}/auth/login", json={"email": "demo@example.com", "password": "wrong"})
    assert res.status_code == 401


def test_me_requires_auth(client, auth_headers):
    assert client.get(f"{API}/auth/me").status_code == 401
    res = client.get(f"{API}/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "demo@example.com"


def test_register_and_duplicate(client):
    import uuid

    username = f"user_{uuid.uuid4().hex[:8]}"
    res = client.post(
        f"{API}/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "secret123", "name": "Test"},
    )
    assert res.status_code == 201
    assert res.json()["user"]["username"] == username

    dup = client.post(
        f"{API}/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "secret123"},
    )
    assert dup.status_code == 400


def test_register_validation(client):
    res = client.post(
        f"{API}/auth/register",
        json={"username": "ab", "email": "not-an-email", "password": "123"},
    )
    assert res.status_code == 422
