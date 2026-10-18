from typing import Optional

from pydantic import BaseModel, Field


class CategoryWrite(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default=None, max_length=60)
    image: Optional[str] = Field(default=None, max_length=1000)


class BrandWrite(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: Optional[str] = Field(default=None, max_length=120)
    country: Optional[str] = Field(default=None, max_length=80)
    logo: Optional[str] = Field(default=None, max_length=1000)
