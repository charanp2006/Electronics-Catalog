"""Comma-separated image URL parsing — the single source of truth.

Both the JSON API and the server-rendered forms funnel through here so the
primary image (``image``) and gallery (``images``) never diverge.
"""
from __future__ import annotations

from typing import List, Optional


def parse_image_urls(csv: Optional[str]) -> List[str]:
    """Split a comma-separated string into a clean, ordered, unique URL list.

    Raises:
        ValueError: if any non-empty entry is not an http(s) URL.
    """
    if not csv:
        return []
    out: List[str] = []
    seen = set()
    for part in csv.split(","):
        url = part.strip()
        if not url:
            continue
        if not url.lower().startswith(("http://", "https://")):
            raise ValueError(f"invalid URL: '{url}'")
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def format_image_urls(images: Optional[List[str]]) -> str:
    return ", ".join(images or [])
