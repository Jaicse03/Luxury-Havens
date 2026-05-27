from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from app.models.hotel import Hotel, HotelImage
from app.models.room import Room
from app.schemas.hotel import HotelCreate, HotelUpdate
from app.schemas.room import RoomCreate, RoomUpdate

def get_hotel(db: Session, hotel_id: int):
    return db.query(Hotel).filter(Hotel.id == hotel_id).first()

def get_hotels(
    db: Session,
    search: Optional[str] = None,
    city: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    amenities: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(Hotel)

    # Search filter (name, description, city, country)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Hotel.name.ilike(search_filter),
                Hotel.description.ilike(search_filter),
                Hotel.city.ilike(search_filter),
                Hotel.country.ilike(search_filter)
            )
        )
    
    if city:
        query = query.filter(Hotel.city.ilike(f"%{city}%"))

    # Price filters (require joining the Room table to check room prices)
    if min_price is not None or max_price is not None:
        query = query.join(Hotel.rooms)
        if min_price is not None:
            query = query.filter(Room.price_per_night >= min_price)
        if max_price is not None:
            query = query.filter(Room.price_per_night <= max_price)

    # Rating filter
    if min_rating is not None:
        query = query.filter(Hotel.rating >= min_rating)

    # Filter by amenities (contains list of amenities)
    if amenities:
        for amenity in amenities:
            # SQLAlchemy JSON list matching
            query = query.filter(Hotel.amenities.contains(amenity))

    # Apply sorting
    if sort_by == "price_asc":
        # Sort by room price ascending
        query = query.order_by(Room.price_per_night.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Room.price_per_night.desc())
    elif sort_by == "rating_desc":
        query = query.order_by(Hotel.rating.desc())
    else:
        query = query.order_by(Hotel.id.desc())

    # De-duplicate if joined with Rooms
    if min_price is not None or max_price is not None or sort_by in ["price_asc", "price_desc"]:
        query = query.distinct()

    return query.offset(skip).limit(limit).all()

# Admin CRUD operations for Hotels
def create_hotel(db: Session, hotel: HotelCreate):
    db_hotel = Hotel(
        name=hotel.name,
        description=hotel.description,
        address=hotel.address,
        city=hotel.city,
        country=hotel.country,
        rating=hotel.rating,
        amenities=hotel.amenities,
        latitude=hotel.latitude,
        longitude=hotel.longitude
    )
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

def update_hotel(db: Session, db_hotel: Hotel, hotel_update: HotelUpdate):
    for key, value in hotel_update.dict(exclude_unset=True).items():
        setattr(db_hotel, key, value)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

def delete_hotel(db: Session, hotel_id: int):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if db_hotel:
        db.delete(db_hotel)
        db.commit()
        return True
    return False

# Room crud
def get_room(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()

def create_room(db: Session, hotel_id: int, room: RoomCreate):
    db_room = Room(
        hotel_id=hotel_id,
        room_type=room.room_type,
        description=room.description,
        price_per_night=room.price_per_night,
        capacity=room.capacity,
        amenities=room.amenities,
        is_available=room.is_available,
        quantity=room.quantity
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def update_room(db: Session, db_room: Room, room_update: RoomUpdate):
    for key, value in room_update.dict(exclude_unset=True).items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room

def delete_room(db: Session, room_id: int):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room:
        db.delete(db_room)
        db.commit()
        return True
    return False
