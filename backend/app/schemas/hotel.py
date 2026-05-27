from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.room import Room

class HotelImageBase(BaseModel):
    url: str
    is_primary: bool = False

class HotelImageCreate(HotelImageBase):
    pass

class HotelImage(HotelImageBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True

class HotelBase(BaseModel):
    name: str
    description: str
    address: str
    city: str
    country: str
    rating: float = 0.0
    amenities: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
    amenities: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Hotel(HotelBase):
    id: int
    created_at: datetime
    images: List[HotelImage] = []
    rooms: List[Room] = []

    class Config:
        from_attributes = True
