from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, index=True, nullable=False)
    country = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    amenities = Column(JSON, default=list)  # Stored as JSON list of strings (e.g. ["Wi-Fi", "Pool"])
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="hotel", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="hotel", cascade="all, delete-orphan")
    images = relationship("HotelImage", back_populates="hotel", cascade="all, delete-orphan")

class HotelImage(Base):
    __tablename__ = "hotel_images"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)

    # Relationships
    hotel = relationship("Hotel", back_populates="images")
