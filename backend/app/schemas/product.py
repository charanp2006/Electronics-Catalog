from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class BrandRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    slug: Optional[str] = None


class CategoryRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    slug: Optional[str] = None


class SpecItem(BaseModel):
    key: str
    value: str


class ReviewItem(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    rating: int
    comment: str
    created_at: Optional[datetime] = None


class PriceHistoryItem(BaseModel):
    old_price: float
    new_price: float
    changed_at: Optional[datetime] = None


class ProductList(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    id: str = Field(alias="_id")
    name: str
    slug: str
    brand: Optional[BrandRef] = None
    category: Optional[CategoryRef] = None
    price: float
    discount_price: Optional[float] = None
    image: Optional[str] = None
    average_rating: float = 0
    total_reviews: int = 0
    stock: int = 0
    is_active: bool = True


class ProductDetail(ProductList):
    description: Optional[str] = None
    specifications: List[SpecItem] = []
    reviews: List[ReviewItem] = []
    price_history: List[PriceHistoryItem] = []
    is_featured: bool = False
