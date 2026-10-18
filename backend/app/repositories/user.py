from typing import Any, Dict, Optional

from bson import ObjectId

from app.db.mongodb import BaseRepository, get_db


class UserRepository(BaseRepository):
    def __init__(self):
        self.collection = get_db()["users"]

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"email": email.lower()})

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"username": username})

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(user_id):
            return None
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def create(self, doc: Dict[str, Any]):
        return self.collection.insert_one(doc)
