from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    room_type = Column(String, nullable=False)  # "Standard", "Deluxe", "Suite", etc.
    description = Column(Text, nullable=False)
    price_per_night = Column(Float, nullable=False)
    capacity = Column(Integer, default=2)  # max guests
    amenities = Column(JSON, default=list)  # ["AC", "TV", "Mini-bar"]
    is_available = Column(Boolean, default=True)
    quantity = Column(Integer, default=5)  # room capacity in hotel

    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")
