from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.api import deps
from app.models.user import User as UserModel
from app.models.hotel import Hotel as HotelModel, HotelImage as HotelImageModel
from app.models.room import Room as RoomModel
from app.models.booking import Booking as BookingModel
from app.models.payment import Payment as PaymentModel
from app.schemas.hotel import Hotel as HotelSchema, HotelCreate, HotelUpdate, HotelImageCreate, HotelImage as HotelImageSchema
from app.schemas.room import Room as RoomSchema, RoomCreate, RoomUpdate
from app.schemas.booking import Booking as BookingSchema
from app.crud import hotel as crud_hotel

router = APIRouter()

# Enforce Admin Role across all routes in this router
dependency_admin = Depends(deps.get_current_active_admin)

@router.post("/hotels", response_model=HotelSchema, dependencies=[dependency_admin])
def admin_create_hotel(
    hotel_in: HotelCreate,
    db: Session = Depends(get_db)
):
    return crud_hotel.create_hotel(db, hotel=hotel_in)

@router.put("/hotels/{id}", response_model=HotelSchema, dependencies=[dependency_admin])
def admin_update_hotel(
    id: int,
    hotel_in: HotelUpdate,
    db: Session = Depends(get_db)
):
    db_hotel = crud_hotel.get_hotel(db, hotel_id=id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return crud_hotel.update_hotel(db, db_hotel=db_hotel, hotel_update=hotel_in)

@router.delete("/hotels/{id}", dependencies=[dependency_admin])
def admin_delete_hotel(
    id: int,
    db: Session = Depends(get_db)
):
    success = crud_hotel.delete_hotel(db, hotel_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Hotel successfully deleted!"}

# Room admin actions
@router.post("/hotels/{hotel_id}/rooms", response_model=RoomSchema, dependencies=[dependency_admin])
def admin_create_room(
    hotel_id: int,
    room_in: RoomCreate,
    db: Session = Depends(get_db)
):
    hotel = crud_hotel.get_hotel(db, hotel_id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return crud_hotel.create_room(db, hotel_id=hotel_id, room=room_in)

@router.put("/rooms/{id}", response_model=RoomSchema, dependencies=[dependency_admin])
def admin_update_room(
    id: int,
    room_in: RoomUpdate,
    db: Session = Depends(get_db)
):
    db_room = crud_hotel.get_room(db, room_id=id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return crud_hotel.update_room(db, db_room=db_room, room_update=room_in)

@router.delete("/rooms/{id}", dependencies=[dependency_admin])
def admin_delete_room(
    id: int,
    db: Session = Depends(get_db)
):
    success = crud_hotel.delete_room(db, room_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room successfully deleted!"}

# Image management for Hotels
@router.post("/hotels/{hotel_id}/images", response_model=HotelImageSchema, dependencies=[dependency_admin])
def admin_add_hotel_image(
    hotel_id: int,
    image_in: HotelImageCreate,
    db: Session = Depends(get_db)
):
    hotel = crud_hotel.get_hotel(db, hotel_id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
        
    db_image = HotelImageModel(
        hotel_id=hotel_id,
        url=image_in.url,
        is_primary=image_in.is_primary
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Bookings admin overview
@router.get("/bookings", response_model=List[BookingSchema], dependencies=[dependency_admin])
def admin_read_all_bookings(
    db: Session = Depends(get_db)
):
    return db.query(BookingModel).order_by(BookingModel.created_at.desc()).all()

# Rich revenue and booking analytics
@router.get("/analytics", dependencies=[dependency_admin])
def admin_get_analytics(
    db: Session = Depends(get_db)
):
    # Total Revenue (Confirmed Bookings)
    total_revenue = db.query(func.sum(BookingModel.total_price)).filter(
        BookingModel.status == "confirmed"
    ).scalar() or 0.0

    # Bookings statuses count
    total_bookings_count = db.query(BookingModel).count()
    confirmed_count = db.query(BookingModel).filter(BookingModel.status == "confirmed").count()
    cancelled_count = db.query(BookingModel).filter(BookingModel.status == "cancelled").count()
    pending_count = db.query(BookingModel).filter(BookingModel.status == "pending").count()

    # User metrics
    total_users_count = db.query(UserModel).filter(UserModel.role == "user").count()

    # Hotel breakdowns (dynamic revenue and average rating grouping)
    hotel_breakdown = []
    hotels = db.query(HotelModel).all()
    for hotel in hotels:
        # Sum revenue for each hotel room booking
        rev = db.query(func.sum(BookingModel.total_price)).join(RoomModel).filter(
            RoomModel.hotel_id == hotel.id,
            BookingModel.status == "confirmed"
        ).scalar() or 0.0
        
        booking_ct = db.query(BookingModel).join(RoomModel).filter(
            RoomModel.hotel_id == hotel.id
        ).count()
        
        hotel_breakdown.append({
            "hotel_id": hotel.id,
            "name": hotel.name,
            "city": hotel.city,
            "rating": hotel.rating,
            "revenue": float(rev),
            "bookings_count": booking_ct
        })

    # Summary metrics
    return {
        "summary": {
            "total_revenue": float(total_revenue),
            "total_bookings": total_bookings_count,
            "confirmed_bookings": confirmed_count,
            "cancelled_bookings": cancelled_count,
            "pending_bookings": pending_count,
            "total_customers": total_users_count,
            "total_hotels": len(hotels)
        },
        "hotels_breakdown": hotel_breakdown
    }
