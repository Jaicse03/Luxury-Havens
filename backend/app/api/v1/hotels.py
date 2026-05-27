from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.api import deps
from app.schemas.hotel import Hotel as HotelSchema
from app.models.booking import Booking as BookingModel
from app.models.room import Room as RoomModel
from app.crud import hotel as crud_hotel

router = APIRouter()

@router.get("/", response_model=List[HotelSchema])
def read_hotels(
    search: Optional[str] = Query(None, description="Search by name, city, or country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_price: Optional[float] = Query(None, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, description="Maximum price per night"),
    min_rating: Optional[float] = Query(None, description="Minimum star rating (e.g. 4.0)"),
    amenities: Optional[List[str]] = Query(None, description="Filter by one or more amenities"),
    sort_by: Optional[str] = Query(None, description="Sort by: price_asc, price_desc, rating_desc"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return crud_hotel.get_hotels(
        db, search=search, city=city, min_price=min_price, max_price=max_price,
        min_rating=min_rating, amenities=amenities, sort_by=sort_by, skip=skip, limit=limit
    )

@router.get("/{id}", response_model=HotelSchema)
def read_hotel(
    id: int,
    db: Session = Depends(get_db)
):
    db_hotel = crud_hotel.get_hotel(db, hotel_id=id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return db_hotel

@router.get("/{id}/availability")
def check_hotel_availability(
    id: int,
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db)
):
    if check_out <= check_in:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")
        
    db_hotel = crud_hotel.get_hotel(db, hotel_id=id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    available_rooms = []
    
    # Check overlapping active bookings for each room of the hotel
    # Overlap logic: booking.check_in < check_out AND booking.check_out > check_in
    for room in db_hotel.rooms:
        overlapping_bookings_count = db.query(BookingModel).filter(
            BookingModel.room_id == room.id,
            BookingModel.status != "cancelled",
            BookingModel.check_in < check_out,
            BookingModel.check_out > check_in
        ).count()
        
        available_qty = max(0, room.quantity - overlapping_bookings_count)
        
        available_rooms.append({
            "room_id": room.id,
            "room_type": room.room_type,
            "price_per_night": room.price_per_night,
            "capacity": room.capacity,
            "amenities": room.amenities,
            "quantity_total": room.quantity,
            "quantity_available": available_qty,
            "is_available": available_qty > 0
        })
        
    return {
        "hotel_id": id,
        "check_in": check_in,
        "check_out": check_out,
        "rooms": available_rooms
    }
