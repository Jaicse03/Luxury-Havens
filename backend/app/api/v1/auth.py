from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.config import settings
from app.schemas.auth import Token, LoginRequest, ForgotPasswordRequest
from app.schemas.user import UserCreate, User as UserSchema
from app.crud import user as crud_user

router = APIRouter()

@router.post("/register", response_model=Token)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    user = crud_user.create_user(db, user=user_in)
    
    # Auto-login after registration
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db)
):
    user = crud_user.get_user_by_email(db, email=login_in.email)
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
def forgot_password(
    req: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    # Mock email verification / recovery link
    user = crud_user.get_user_by_email(db, email=req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {"message": f"Password reset instructions sent to {req.email} (mocked)"}

@router.post("/verify-email")
def verify_email(
    email: str,
    db: Session = Depends(get_db)
):
    # Mock email verification trigger
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    return {"message": "Email successfully verified!"}
