from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.api import deps
from app.models.user import User as UserModel
from app.models.room import Room as RoomModel
from app.models.booking import Booking as BookingModel
from app.schemas.booking import Booking as BookingSchema, BookingCreate
from app.schemas.payment import Payment as PaymentSchema, PaymentCreate
from app.crud import booking as crud_booking

router = APIRouter()

@router.post("/", response_model=BookingSchema)
def make_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    # Verify room exists
    room = db.query(RoomModel).filter(RoomModel.id == booking_in.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if booking_in.check_out <= booking_in.check_in:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    # Double check room availability for overlap
    overlapping_bookings = db.query(BookingModel).filter(
        BookingModel.room_id == booking_in.room_id,
        BookingModel.status != "cancelled",
        BookingModel.check_in < booking_in.check_out,
        BookingModel.check_out > booking_in.check_in
    ).count()

    if overlapping_bookings >= room.quantity:
        raise HTTPException(
            status_code=400,
            detail="Sorry, this room type is fully booked for the selected dates."
        )

    try:
        booking = crud_booking.create_booking(db, user_id=current_user.id, booking=booking_in)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-bookings", response_model=List[BookingSchema])
def read_my_bookings(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    return crud_booking.get_bookings_by_user(db, user_id=current_user.id)

@router.get("/{id}", response_model=BookingSchema)
def read_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    booking = crud_booking.get_booking(db, booking_id=id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Check permissions (owner or admin)
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
        
    return booking

@router.post("/{id}/pay", response_model=PaymentSchema)
def pay_booking(
    id: int,
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    booking = crud_booking.get_booking(db, booking_id=id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")
        
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail=f"Booking is already {booking.status}")

    # Complete mock payment
    payment = crud_booking.create_payment(db, payment=payment_in, amount=booking.total_price)
    return payment

@router.put("/{id}/cancel", response_model=BookingSchema)
def cancel_booking(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    booking = crud_booking.get_booking(db, booking_id=id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Check permissions
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
        
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    updated_booking = crud_booking.update_booking_status(db, booking_id=id, status="cancelled")
    return updated_booking

@router.get("/{id}/invoice")
def get_invoice(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    booking = crud_booking.get_booking(db, booking_id=id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access invoice")
        
    # Generate structured invoice payload
    nights = (booking.check_out - booking.check_in).days
    room = booking.room
    hotel = room.hotel
    
    return {
        "invoice_number": f"INV-{booking.booking_code.split('-')[1]}-{booking.id}",
        "booking_code": booking.booking_code,
        "date_issued": booking.created_at.date().isoformat(),
        "customer": {
            "name": booking.guest_name,
            "email": booking.guest_email,
            "user_id": booking.user_id
        },
        "hotel": {
            "name": hotel.name,
            "address": hotel.address,
            "location": f"{hotel.city}, {hotel.country}"
        },
        "stay": {
            "room_type": room.room_type,
            "check_in": booking.check_in.isoformat(),
            "check_out": booking.check_out.isoformat(),
            "nights": nights,
            "price_per_night": room.price_per_night,
            "guest_count": booking.guest_count
        },
        "payment": {
            "status": "PAID" if booking.status == "confirmed" else "UNPAID",
            "total_price": booking.total_price,
            "currency": "USD"
        }
    }
