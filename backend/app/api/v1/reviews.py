from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api import deps
from app.models.user import User as UserModel
from app.models.booking import Booking as BookingModel
from app.models.room import Room as RoomModel
from app.schemas.review import Review as ReviewSchema, ReviewCreate
from app.crud import review as crud_review

router = APIRouter()

@router.get("/hotel/{hotel_id}", response_model=List[ReviewSchema])
def read_hotel_reviews(
    hotel_id: int,
    db: Session = Depends(get_db)
):
    return crud_review.get_reviews_by_hotel(db, hotel_id=hotel_id)

@router.post("/", response_model=ReviewSchema)
def create_user_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    # Verify authenticity: check if this user has booked a room in this hotel
    user_has_stay = db.query(BookingModel).join(RoomModel).filter(
        BookingModel.user_id == current_user.id,
        RoomModel.hotel_id == review_in.hotel_id,
        BookingModel.status == "confirmed"
    ).first()

    if not user_has_stay:
        raise HTTPException(
            status_code=400,
            detail="To submit a review, you must have a confirmed reservation at this hotel."
        )

    return crud_review.create_review(db, user_id=current_user.id, review=review_in)
