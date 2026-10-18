"""Slug generation & uniqueness."""
from __future__ import annotations

import re
from typing import Optional

from bson import ObjectId

_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    value = _slug_re.sub("-", (name or "").strip().lower())
    return value.strip("-")


def unique_slug(collection, base: str, exclude_id: Optional[str] = None) -> str:
    """Return ``base`` if free, else ``base-2``, ``base-3`` … until unique."""
    root = slugify(base) or "item"
    query_extra = {}
    if exclude_id and ObjectId.is_valid(exclude_id):
        query_extra = {"_id": {"$ne": ObjectId(exclude_id)}}

    candidate = root
    n = 1
    while collection.find_one({"slug": candidate, **query_extra}, {"_id": 1}):
        n += 1
        candidate = f"{root}-{n}"
    return candidate
