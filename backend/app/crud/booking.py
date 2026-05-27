from sqlalchemy.orm import Session
from datetime import date
import uuid
import random
from app.models.booking import Booking
from app.models.room import Room
from app.models.payment import Payment
from app.schemas.booking import BookingCreate
from app.schemas.payment import PaymentCreate

def get_booking(db: Session, booking_id: int):
    return db.query(Booking).filter(Booking.id == booking_id).first()

def get_booking_by_code(db: Session, code: str):
    return db.query(Booking).filter(Booking.booking_code == code).first()

def get_bookings_by_user(db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()

def get_all_bookings(db: Session):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()

def create_booking(db: Session, user_id: int, booking: BookingCreate):
    # Retrieve room price
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise ValueError("Room not found")
        
    # Calculate price based on nights
    nights = (booking.check_out - booking.check_in).days
    if nights <= 0:
        raise ValueError("Check-out date must be after check-in date")
        
    total_price = nights * room.price_per_night

    # Generate unique short alphanumeric reservation code (e.g. LH-9F4D2E)
    code_suffix = uuid.uuid4().hex[:6].upper()
    booking_code = f"LH-{code_suffix}"

    db_booking = Booking(
        booking_code=booking_code,
        user_id=user_id,
        room_id=booking.room_id,
        check_in=booking.check_in,
        check_out=booking.check_out,
        total_price=total_price,
        status="pending",
        guest_name=booking.guest_name,
        guest_email=booking.guest_email,
        guest_count=booking.guest_count
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def update_booking_status(db: Session, booking_id: int, status: str):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking:
        db_booking.status = status
        db.commit()
        db.refresh(db_booking)
    return db_booking

def create_payment(db: Session, payment: PaymentCreate, amount: float):
    # Generate random transaction ID if not provided
    transaction_id = payment.transaction_id or f"TX-{uuid.uuid4().hex[:12].upper()}"
    
    db_payment = Payment(
        booking_id=payment.booking_id,
        transaction_id=transaction_id,
        amount=amount,
        payment_method=payment.payment_method,
        status="success"  # default to successful simulation
    )
    db.add(db_payment)
    
    # Update associated booking to "confirmed" on successful mock payment
    db_booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if db_booking:
        db_booking.status = "confirmed"
        db.add(db_booking)
        
    db.commit()
    db.refresh(db_payment)
    return db_payment
