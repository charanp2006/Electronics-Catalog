from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class SpecItem(BaseModel):
    key: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=300)


class ProductWrite(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=220)
    brand: str = Field(min_length=1)
    category: str = Field(min_length=1)
    description: Optional[str] = Field(default=None, max_length=5000)
    price: float = Field(gt=0)
    discount_price: Optional[float] = Field(default=None, gt=0)
    stock: int = Field(default=0, ge=0)
    image_urls: Optional[str] = None
    specifications: List[SpecItem] = []
    is_active: bool = True
    is_featured: bool = False

    @model_validator(mode="after")
    def _check_discount(self):
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("discount_price must be less than price")
        return self


class ProductPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=220)
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=5000)
    price: Optional[float] = Field(default=None, gt=0)
    discount_price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    image_urls: Optional[str] = None
    specifications: Optional[List[SpecItem]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
