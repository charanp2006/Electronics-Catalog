from __future__ import annotations

import time
from functools import wraps

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import AutoReconnect, ConnectionFailure, NetworkTimeout

from app.core.config import settings

_client: MongoClient | None = None
_db: Database | None = None

# Connection-pool and timeout tuning. Applied as client options (not via the URI)
# so they hold no matter which connection string is pasted in .env:
#   - fail fast instead of hanging ~30s when the cluster is unreachable
#   - drop sockets that have been idle, so we never try to reuse one that the
#     server / network / a sleeping host already closed
CLIENT_OPTIONS = {
    "serverSelectionTimeoutMS": 5000,
    "connectTimeoutMS": 10000,
    "socketTimeoutMS": 45000,
    "maxPoolSize": 50,
    "minPoolSize": 0,
    "maxIdleTimeMS": 45000,
}

RETRYABLE_ERRORS = (AutoReconnect, ConnectionFailure, NetworkTimeout)


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri, **CLIENT_OPTIONS)
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[settings.MONGODB_DB_NAME]
    return _db


def close_client() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None


def retry_once(func):
    """Retry a repository operation once if the connection was dropped.

    PyMongo's topology monitor reconnects on its own; this simply absorbs the
    first failed attempt after an idle period so callers never see it.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RETRYABLE_ERRORS:
            time.sleep(0.4)
            return func(*args, **kwargs)

    return wrapper


class BaseRepository:
    """Auto-retries read operations once when a connection drops.

    Only read-style methods (get*/list*/featured/related/raw*) are wrapped.
    Writes are already retried by the driver (``retryWrites=true``); retrying
    them here could double-apply a non-idempotent change such as decrementing
    stock twice, so they are intentionally left alone.
    """

    _READ_PREFIXES = ("get", "list", "featured", "related", "raw")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in list(vars(cls).items()):
            if (
                callable(value)
                and not name.startswith("_")
                and name.startswith(cls._READ_PREFIXES)
            ):
                setattr(cls, name, retry_once(value))
