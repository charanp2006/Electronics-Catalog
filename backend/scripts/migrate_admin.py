#!/usr/bin/env python3
"""Idempotent migration to add Admin CMS support to an existing database.

Safe to run multiple times. It:

* ensures ``users.is_admin`` / ``users.role`` exist,
* promotes (or creates) an admin account from ``ADMIN_EMAIL``/``ADMIN_PASSWORD``,
* backfills ``orders.status`` / ``status_history`` / ``updated_at``,
* backfills ``reviews[].review_id`` / ``status`` / ``updated_at`` and
  recomputes ``average_rating`` / ``total_reviews`` from published reviews,
* creates the indexes the admin UI relies on.

Usage:
    python scripts/migrate_admin.py
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402

load_dotenv()


def now() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


client = MongoClient(settings.mongo_uri)
db = client[settings.MONGODB_DB_NAME]

summary = {}

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
users = db.users
result = users.update_many(
    {"is_admin": {"$exists": False}},
    {"$set": {"is_admin": False, "role": "customer"}},
)
users.update_many({"role": {"$exists": False}}, {"$set": {"role": "customer"}})
summary["users_tagged"] = result.modified_count

admin_email = os.getenv("ADMIN_EMAIL")
admin_password = os.getenv("ADMIN_PASSWORD")
if not admin_email or not admin_password:
    raise RuntimeError("ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment")
existing = users.find_one({"email": admin_email.lower()})
if existing:
    users.update_one(
        {"_id": existing["_id"]},
        {"$set": {"is_admin": True, "role": "admin", "is_active": True}},
    )
    admin_state = f"promoted existing user {admin_email}"
else:
    users.insert_one(
        {
            "username": "admin",
            "name": "Administrator",
            "email": admin_email.lower(),
            "password": hash_password(admin_password),
            "is_active": True,
            "is_admin": True,
            "role": "admin",
            "created_at": now(),
        }
    )
    admin_state = f"created admin {admin_email}"

# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
orders = client[settings.MONGODB_DB_NAME]["orders"]
order_updates = 0
for order in orders.find({"status": {"$exists": False}}):
    created = order.get("created_at", now())
    orders.update_one(
        {"_id": order["_id"]},
        {
            "$set": {
                "status": "pending",
                "status_history": [{"status": "pending", "at": created, "by": "migration"}],
                "updated_at": created,
            }
        },
    )
    order_updates += 1

# ---------------------------------------------------------------------------
# Products / embedded reviews
# ---------------------------------------------------------------------------
products = client[settings.MONGODB_DB_NAME]["products"]
review_updates = 0
for product in products.find({}, {"reviews": 1}):
    reviews = product.get("reviews", [])
    changed = False
    for review in reviews:
        if "review_id" not in review:
            review["review_id"] = uuid4().hex
            changed = True
        if "status" not in review:
            review["status"] = "published"
            changed = True
        if "updated_at" not in review:
            review["updated_at"] = review.get("created_at", now())
            changed = True
    published = [r for r in reviews if r.get("status", "published") == "published"]
    avg = round(sum(r.get("rating", 0) for r in published) / len(published), 2) if published else 0
    products.update_one(
        {"_id": product["_id"]},
        {
            "$set": {
                "reviews": reviews,
                "average_rating": avg,
                "total_reviews": len(published),
            }
        },
    )
    if changed:
        review_updates += 1

# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------
users.create_index("is_admin")
orders.create_index("status")
orders.create_index("created_at")
client[settings.MONGODB_DB_NAME]["audit_logs"].create_index("at")

print("Migration complete")
print(f"  users tagged:   {users.count_documents({'role': {'$exists': True}})}")
print(f"  admin account:  {admin_state}")
print(f"  orders updated: {order_updates}")
print(f"  products with reviews touched: {review_updates}")
client.close()
