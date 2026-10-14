from datetime import datetime
from typing import Any

from bson import ObjectId


def serialize(value: Any) -> Any:
    """Recursively convert BSON types into JSON-serializable values."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(v) for v in value]
    return value
