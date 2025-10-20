from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import random

from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, UserResponse, UserLogin, Token
from backend.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


def generate_student_id():
    """Generate a unique student ID"""
    return f"HS{random.randint(10000, 99999)}"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate student ID
    student_id = generate_student_id()
    while get_user_by_student_id(db, student_id):
        student_id = generate_student_id()
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        student_id=student_id,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        major=user_data.major,
        program=user_data.program,
        career_goal=user_data.career_goal,
        experience_level=user_data.experience_level
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = get_user_by_email(db, user_credentials.email)
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login endpoint"""
    user = get_user_by_email(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


def get_user_by_student_id(db: Session, student_id: str):
    """Get user by student ID"""
    return db.query(User).filter(User.student_id == student_id).first()
