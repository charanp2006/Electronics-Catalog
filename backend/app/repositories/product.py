from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.db.mongodb import get_db

class ProductRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db["products"]

    def list_products(self, q: Optional[str] = None, category: Optional[str] = None,
                      brand: Optional[str] = None, min_price: Optional[float] = None,
                      max_price: Optional[float] = None, sort: str = "newest",
                      page: int = 1, limit: int = 12) -> Dict[str, Any]:
        query = {"is_active": True}
        if q:
            query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"brand.name": {"$regex": q, "$options": "i"}},
                {"specifications.value": {"$regex": q, "$options": "i"}}
            ]
        if category:
            query["$or"] = query.get("$or", [])
            query["$or"].append({"category._id": category})
            query["$or"].append({"category.name": {"$regex": category, "$options": "i"}})
        if brand:
            query["$or2"] = [{"brand._id": brand}, {"brand.name": {"$regex": brand, "$options": "i"}}]
        price_q = {}
        if min_price is not None:
            price_q["$gte"] = min_price
        if max_price is not None:
            price_q["$lte"] = max_price
        if price_q:
            query["$expr"] = {
                "$lte": [
                    {"$ifNull": ["$discount_price", "$price"]},
                    price_q.get("$lte", 10**12)
                ]
            }
            # simpler: check current price via price/discount
            # handle range properly
            query["$and"] = []
            cp_low = {}
            if min_price is not None:
                cp_low["$gte"] = min_price
            if cp_low:
                query["$and"].append({"$or": [
                    {"discount_price": {"$ne": None, **cp_low}},
                    {"discount_price": None, "price": cp_low}
                ]})
            cp_high = {}
            if max_price is not None:
                cp_high["$lte"] = max_price
            if cp_high:
                if "$and" not in query:
                    query["$and"] = []
                query["$and"].append({"$or": [
                    {"discount_price": {"$ne": None, **cp_high}},
                    {"discount_price": None, "price": cp_high}
                ]})
            if category and brand:
                pass
        # clean up temp
        if brand:
            query["$or"] = [{"brand._id": brand}, {"brand.name": {"$regex": brand, "$options": "i"}}]
        if category and brand is None:
            query["$or"] = [{"category._id": category}, {"category.name": {"$regex": category, "$options": "i"}}]

        # rebuild cleanly
        qf = {"is_active": True}
        ors = []
        if q:
            ors.append({"name": {"$regex": q, "$options": "i"}})
            ors.append({"description": {"$regex": q, "$options": "i"}})
            ors.append({"brand.name": {"$regex": q, "$options": "i"}})
            ors.append({"specifications.value": {"$regex": q, "$options": "i"}})
        if ors:
            qf["$or"] = ors
        if category:
            qf["category.name"] = {"$regex": category, "$options": "i"}
        if brand:
            qf["brand.name"] = {"$regex": brand, "$options": "i"}
        ands = []
        if min_price is not None:
            ands.append({"$or": [
                {"discount_price": {"$gte": min_price}},
                {"discount_price": {"$eq": None}, "price": {"$gte": min_price}}
            ]})
        if max_price is not None:
            ands.append({"$or": [
                {"discount_price": {"$lte": max_price}},
                {"discount_price": {"$eq": None}, "price": {"$lte": max_price}}
            ]})
        if ands:
            qf["$and"] = ands

        sort_map = {
            "price_asc": [("price", 1), ("discount_price", 1)],
            "price_desc": [("discount_price", -1), ("price", -1)],
            "rating_desc": [("average_rating", -1)],
            "newest": [("created_at", -1)]
        }
        skip = (page - 1) * limit
        cursor = self.collection.find(qf, {"specifications": 0, "reviews": 0, "price_history": 0}).sort(sort_map.get(sort, [("created_at", -1)])).skip(skip).limit(limit)
        items = []
        for d in cursor:
            d["_id"] = str(d["_id"])
            if d.get("brand") and isinstance(d["brand"].get("_id"), ObjectId):
                d["brand"]["_id"] = str(d["brand"]["_id"])
            if d.get("category") and isinstance(d["category"].get("_id"), ObjectId):
                d["category"]["_id"] = str(d["category"]["_id"])
            items.append(d)
        total = self.collection.count_documents(qf)
        return {"items": items, "total": total, "page": page, "limit": limit}

    def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        d = self.collection.find_one({"slug": slug})
        if not d:
            return None
        d["_id"] = str(d["_id"])
        if d.get("brand") and isinstance(d["brand"].get("_id"), ObjectId):
            d["brand"]["_id"] = str(d["brand"]["_id"])
        if d.get("category") and isinstance(d["category"].get("_id"), ObjectId):
            d["category"]["_id"] = str(d["category"]["_id"])
        for r in d.get("reviews", []):
            if isinstance(r.get("_id"), ObjectId):
                r["_id"] = str(r["_id"])
        return d
