from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class BrandRef(BaseModel):
    _id: str
    name: str

class CategoryRef(BaseModel):
    _id: str
    name: str

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
    _id: str
    name: str
    slug: str
    brand: Optional[BrandRef] = None
    category: Optional[CategoryRef] = None
    price: float
    discount_price: Optional[float] = None
    image: Optional[str] = None
    average_rating: float
    total_reviews: int
    stock: int
    is_active: bool

class ProductDetail(ProductList):
    description: str
    specifications: List[SpecItem] = []
    reviews: List[ReviewItem] = []
    price_history: List[PriceHistoryItem] = []
    is_featured: bool
