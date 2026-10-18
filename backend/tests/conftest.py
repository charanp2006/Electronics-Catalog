import os
import subprocess
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

from app.main import app  # noqa: E402

API = "/api/v1"

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin12345")


def _seed():
    subprocess.run(
        [sys.executable, str(BACKEND_DIR / "seed.py")],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
        stdin=subprocess.DEVNULL,
    )


@pytest.fixture(scope="session", autouse=True)
def seeded_database():
    _seed()
    yield
    _seed()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    res = client.post(
        f"{API}/auth/login",
        json={"email": "demo@example.com", "password": "demo12345"},
    )
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def admin_headers(client):
    res = client.post(
        f"{API}/admin/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def first_product(client):
    return client.get(f"{API}/products/").json()["items"][0]
