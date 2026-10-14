from fastapi import APIRouter
from app.db.mongodb import get_db
from bson import ObjectId

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/")
def list_categories():
    db = get_db()
    coll = db["categories"]
    items = []
    for d in coll.find():
        d["_id"] = str(d["_id"])
        items.append(d)
    return items
