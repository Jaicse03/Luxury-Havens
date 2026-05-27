from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"

# Properties to receive on user creation
class UserCreate(UserBase):
    email: EmailStr
    full_name: str
    password: str

# Properties to receive on user update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 support for standard ORM object parsing (orm_mode = True in v1)

# Properties to return to client
class User(UserInDBBase):
    pass
