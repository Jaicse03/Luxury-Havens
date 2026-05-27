from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.review import Review
from app.models.hotel import Hotel
from app.schemas.review import ReviewCreate

def get_reviews_by_hotel(db: Session, hotel_id: int):
    return db.query(Review).filter(Review.hotel_id == hotel_id).order_by(Review.created_at.desc()).all()

def create_review(db: Session, user_id: int, review: ReviewCreate):
    db_review = Review(
        user_id=user_id,
        hotel_id=review.hotel_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # Recalculate and update the aggregate hotel rating in background
    recalculate_hotel_rating(db, review.hotel_id)
    
    return db_review

def recalculate_hotel_rating(db: Session, hotel_id: int):
    # Calculate the average rating
    result = db.query(func.avg(Review.rating)).filter(Review.hotel_id == hotel_id).scalar()
    
    # Get the hotel and update
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if hotel and result is not None:
        hotel.rating = round(float(result), 1)
        db.add(hotel)
        db.commit()
