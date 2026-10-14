from fastapi import APIRouter
from app.db.mongodb import get_db
from bson import ObjectId

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/")
def list_brands():
    db = get_db()
    coll = db["brands"]
    items = []
    for d in coll.find():
        d["_id"] = str(d["_id"])
        items.append(d)
    return items
