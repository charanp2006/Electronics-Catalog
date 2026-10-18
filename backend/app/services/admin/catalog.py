from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException

from app.repositories.brand import BrandRepository
from app.repositories.category import CategoryRepository
from app.schemas.admin.catalog import BrandWrite, CategoryWrite
from app.services.admin import audit
from app.services.admin.slug import unique_slug
from app.utils.serialization import serialize


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()

    def list(self, q: Optional[str] = None) -> list:
        return self.repo.list_admin(q)

    def get(self, category_id: str) -> dict:
        doc = self.repo.get_by_id(category_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Category not found")
        return doc

    def create(self, payload: CategoryWrite, actor: dict, ip: Optional[str] = None) -> dict:
        now = _now()
        doc = {
            "name": payload.name,
            "slug": unique_slug(self.repo.collection, payload.slug or payload.name),
            "description": payload.description,
            "icon": payload.icon,
            "image": payload.image,
            "created_at": now,
            "updated_at": now,
        }
        inserted = self.repo.create(doc)
        doc["_id"] = inserted.inserted_id
        audit.log(actor, "category.create", "category", inserted.inserted_id, payload.name, ip=ip)
        return serialize(doc)

    def update(self, category_id: str, payload: CategoryWrite, actor: dict, ip: Optional[str] = None) -> dict:
        if not self.repo.get_by_id(category_id):
            raise HTTPException(status_code=404, detail="Category not found")
        updates = {
            "name": payload.name,
            "slug": unique_slug(self.repo.collection, payload.slug or payload.name, exclude_id=category_id),
            "description": payload.description,
            "icon": payload.icon,
            "image": payload.image,
            "updated_at": _now(),
        }
        self.repo.update(category_id, updates)
        audit.log(actor, "category.update", "category", category_id, payload.name)
        return self.repo.get_by_id(category_id)

    def delete(self, category_id: str, actor: dict, ip: Optional[str] = None) -> dict:
        existing = self.repo.get_by_id(category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Category not found")
        count = self.repo.product_count(existing["slug"])
        if count > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete: {count} product(s) reference this category",
            )
        self.repo.delete(category_id)
        audit.log(actor, "category.delete", "category", category_id, existing.get("name"), ip=ip)
        return {"deleted": True}


class BrandService:
    def __init__(self):
        self.repo = BrandRepository()

    def list(self, q: Optional[str] = None) -> list:
        return self.repo.list_admin(q)

    def create(self, payload: BrandWrite, actor: dict, ip: Optional[str] = None) -> dict:
        slug = unique_slug(self.repo.collection, payload.slug or payload.name)
        now = _now()
        doc = {
            "name": payload.name,
            "slug": slug,
            "country": payload.country,
            "logo": payload.logo,
            "created_at": now,
            "updated_at": now,
        }
        inserted = self.repo.create(doc)
        doc["_id"] = inserted.inserted_id
        audit.log(actor, "brand.create", "brand", inserted.inserted_id, payload.name, ip=ip)
        return serialize(doc)

    def update(self, brand_id: str, payload: BrandWrite, actor: dict, ip: Optional[str] = None) -> dict:
        if not self.repo.get_by_id(brand_id):
            raise HTTPException(status_code=404, detail="Brand not found")
        updates = {
            "name": payload.name,
            "slug": unique_slug(self.repo.collection, payload.slug or payload.name, exclude_id=brand_id),
            "country": payload.country,
            "logo": payload.logo,
            "updated_at": _now(),
        }
        self.repo.update(brand_id, updates)
        audit.log(actor, "brand.update", "brand", brand_id, payload.name, ip=ip)
        return self.repo.get_by_id(brand_id)

    def delete(self, brand_id: str, actor: dict, ip: Optional[str] = None) -> dict:
        existing = self.repo.get_by_id(brand_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Brand not found")
        count = self.repo.product_count(existing["slug"])
        if count > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete: {count} product(s) reference this brand",
            )
        self.repo.delete(brand_id)
        audit.log(actor, "brand.delete", "brand", brand_id, existing.get("name"), ip=ip)
        return {"deleted": True}
