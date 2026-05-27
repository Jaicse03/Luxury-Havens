from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewUserMini(BaseModel):
    full_name: str

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    hotel_id: int
    rating: int = Field(..., ge=1, le=5)  # Constrained rating between 1 and 5
    comment: str

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Review(ReviewBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[ReviewUserMini] = None

    class Config:
        from_attributes = True
