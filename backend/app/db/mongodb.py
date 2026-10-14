from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings

_client = None
_db = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = settings.MONGODB_URI_LOCAL if settings.ENV.lower() == "local" else settings.MONGODB_URI_ATLAS
        _client = MongoClient(uri)
    return _client

def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[settings.MONGODB_DB_NAME]
    return _db

def close_client():
    global _client
    if _client is not None:
        _client.close()
        _client = None
