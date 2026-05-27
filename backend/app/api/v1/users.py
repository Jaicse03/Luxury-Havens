from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api import deps
from app.models.user import User as UserModel
from app.models.favorite import Favorite as FavoriteModel
from app.models.hotel import Hotel as HotelModel
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.hotel import Hotel as HotelSchema
from app.crud import user as crud_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_user)
):
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    return crud_user.update_user(db, db_user=current_user, user_update=user_in)

@router.get("/me/favorites", response_model=List[HotelSchema])
def get_user_favorites(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    # Fetch all favorites and retrieve matching hotels
    favorites = db.query(FavoriteModel).filter(FavoriteModel.user_id == current_user.id).all()
    hotel_ids = [fav.hotel_id for fav in favorites]
    
    hotels = db.query(HotelModel).filter(HotelModel.id.in_(hotel_ids)).all() if hotel_ids else []
    return hotels

@router.post("/me/favorites/{hotel_id}")
def toggle_favorite(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    # Check if hotel exists
    hotel = db.query(HotelModel).filter(HotelModel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
        
    # Check if already favorited
    fav = db.query(FavoriteModel).filter(
        FavoriteModel.user_id == current_user.id,
        FavoriteModel.hotel_id == hotel_id
    ).first()
    
    if fav:
        db.delete(fav)
        db.commit()
        return {"favorited": False, "message": "Removed from favorites"}
    else:
        new_fav = FavoriteModel(user_id=current_user.id, hotel_id=hotel_id)
        db.add(new_fav)
        db.commit()
        return {"favorited": True, "message": "Added to favorites"}
