"""Best-effort audit logging for admin mutations."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.mongodb import get_db

logger = logging.getLogger("electrohub.audit")


def log(
    actor: Dict[str, Any],
    action: str,
    entity: str,
    entity_id: Optional[str] = None,
    summary: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    ip: Optional[str] = None,
    surface: str = "B",
) -> None:
    try:
        get_db()["audit_logs"].insert_one(
            {
                "actor_id": str(actor.get("_id")) if actor else None,
                "actor_username": (actor or {}).get("username"),
                "action": action,
                "entity": entity,
                "entity_id": str(entity_id) if entity_id is not None else None,
                "summary": summary,
                "changes": changes,
                "ip": ip,
                "surface": surface,
                "at": datetime.now(timezone.utc),
            }
        )
    except Exception:  # pragma: no cover - never block the operation
        logger.warning("audit log failed for action=%s", action, exc_info=True)
