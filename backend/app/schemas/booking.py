from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from app.schemas.room import Room

class BookingBase(BaseModel):
    room_id: int
    check_in: date
    check_out: date
    guest_name: str
    guest_email: EmailStr
    guest_count: int = 1

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[str] = None  # "pending", "confirmed", "cancelled"

# Simplified hotel detail for nested display in dashboard booking card
class HotelMini(BaseModel):
    id: int
    name: str
    city: str
    country: str
    
    class Config:
        from_attributes = True

# Extended Room mapping that carries hotel mini details
class RoomWithHotel(Room):
    hotel: Optional[HotelMini] = None

    class Config:
        from_attributes = True

class Booking(BookingBase):
    id: int
    booking_code: str
    total_price: float
    status: str
    user_id: int
    created_at: datetime
    room: Optional[RoomWithHotel] = None

    class Config:
        from_attributes = True
