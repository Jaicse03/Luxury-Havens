from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        hashed_password=hashed_pw,
        role=user.role or "user",
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_update: UserUpdate):
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.phone is not None:
        db_user.phone = user_update.phone
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
