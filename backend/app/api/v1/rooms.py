from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.room import Room as RoomSchema
from app.crud import hotel as crud_hotel

router = APIRouter()

@router.get("/{id}", response_model=RoomSchema)
def read_room(
    id: int,
    db: Session = Depends(get_db)
):
    db_room = crud_hotel.get_room(db, room_id=id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room
