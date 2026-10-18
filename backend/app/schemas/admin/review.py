from typing import Optional

from pydantic import BaseModel, Field


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    status: Optional[str] = Field(default=None, pattern="^(published|hidden)$")
