from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.repositories.brand import BrandRepository
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository
from app.schemas.admin.product import ProductPatch, ProductWrite
from app.services.admin import audit
from app.services.admin.images import format_image_urls, parse_image_urls
from app.services.admin.slug import slugify, unique_slug
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProductService:
    def __init__(self):
        self.repo = ProductRepository()
        self.brands = BrandRepository()
        self.categories = CategoryRepository()

    def _resolve_ref(self, kind: str, value: str) -> Dict[str, Any]:
        collection = self.brands.collection if kind == "brand" else self.categories.collection
        doc = None
        if ObjectId.is_valid(value):
            doc = collection.find_one({"_id": ObjectId(value)})
        if not doc:
            doc = collection.find_one({"slug": value}) or collection.find_one(
                {"slug": slugify(value)}
            )
        if not doc:
            raise HTTPException(status_code=400, detail=f"{kind} not found: {value}")
        return {"_id": doc["_id"], "name": doc["name"], "slug": doc.get("slug")}

    def _images(self, csv: Optional[str]):
        try:
            return parse_image_urls(csv)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    def _fields(self, payload: ProductWrite) -> Dict[str, Any]:
        images = self._images(payload.image_urls)
        return {
            "name": payload.name,
            "brand": self._resolve_ref("brand", payload.brand),
            "category": self._resolve_ref("category", payload.category),
            "description": payload.description,
            "price": payload.price,
            "discount_price": payload.discount_price,
            "stock": payload.stock,
            "image": images[0] if images else None,
            "images": images,
            "specifications": [s.model_dump() for s in payload.specifications],
            "is_active": payload.is_active,
            "is_featured": payload.is_featured,
        }

    def create(self, payload: ProductWrite, actor: dict, ip: Optional[str] = None) -> dict:
        slug = unique_slug(self.repo.collection, payload.slug or payload.name)
        now = _now()
        doc = self._fields(payload)
        doc.update(
            {
                "slug": slug,
                "reviews": [],
                "price_history": [],
                "average_rating": 0,
                "total_reviews": 0,
                "created_at": now,
                "updated_at": now,
            }
        )
        inserted = self.repo.create(doc)
        doc["_id"] = inserted.inserted_id
        audit.log(actor, "product.create", "product", inserted.inserted_id, payload.name, ip=ip)
        return serialize(doc)

    def update(self, product_id: str, payload: ProductWrite, actor: dict, ip: Optional[str] = None) -> dict:
        existing = self.repo.get_by_id_raw(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        updates = self._fields(payload)
        updates["slug"] = unique_slug(
            self.repo.collection, payload.slug or payload.name, exclude_id=product_id
        )
        updates["updated_at"] = _now()

        old_price = existing.get("price")
        if old_price is not None and float(old_price) != float(payload.price):
            history = existing.get("price_history", [])
            history.append(
                {"old_price": old_price, "new_price": payload.price, "changed_at": updates["updated_at"]}
            )
            updates["price_history"] = history

        self.repo.update(product_id, updates)
        audit.log(actor, "product.update", "product", product_id, payload.name, ip=ip)
        return self.repo.get_by_id(product_id)

    def patch(self, product_id: str, changes: Dict[str, Any], actor: dict, ip: Optional[str] = None) -> dict:
        existing = self.repo.get_by_id_raw(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")
        merged = {
            "name": existing.get("name"),
            "slug": existing.get("slug"),
            "brand": existing.get("brand", {}).get("slug"),
            "category": existing.get("category", {}).get("slug"),
            "description": existing.get("description"),
            "price": existing.get("price"),
            "discount_price": existing.get("discount_price"),
            "stock": existing.get("stock", 0),
            "image_urls": format_image_urls(existing.get("images")),
            "specifications": existing.get("specifications", []),
            "is_active": existing.get("is_active", True),
            "is_featured": existing.get("is_featured", False),
        }
        merged.update(changes)
        payload = ProductWrite(**merged)
        return self.update(product_id, payload, actor, ip)

    def delete(self, product_id: str, actor: dict, hard: bool = False, ip: Optional[str] = None) -> dict:
        existing = self.repo.get_by_id_raw(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")
        if hard:
            self.repo.delete(product_id)
        else:
            self.repo.update(product_id, {"is_active": False, "updated_at": _now()})
        audit.log(
            actor,
            "product.delete" if hard else "product.deactivate",
            "product",
            product_id,
            existing.get("name"),
            ip=ip,
        )
        return {"deleted": True, "hard": hard}

    def get(self, product_id: str) -> dict:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def list(self, **filters) -> dict:
        return self.repo.list_admin(**filters)
