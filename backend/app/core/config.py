import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeythatisverysecureandlong1234567890!@#")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week for easy testing and persistency
    PROJECT_NAME: str = "Luxury Havens"
    
    # SQLite default, or PostgreSQL if configured
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hotel_booking.db")
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        case_sensitive = True

settings = Settings()
