from pydantic import BaseModel
from typing import List, Optional

class RoomBase(BaseModel):
    room_type: str
    description: str
    price_per_night: float
    capacity: int
    amenities: List[str] = []
    is_available: bool = True
    quantity: int = 5

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_type: Optional[str] = None
    description: Optional[str] = None
    price_per_night: Optional[float] = None
    capacity: Optional[int] = None
    amenities: Optional[List[str]] = None
    is_available: Optional[bool] = None
    quantity: Optional[int] = None

class Room(RoomBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True
