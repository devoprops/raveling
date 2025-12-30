"""Authentication API routes."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.database.database import get_db
from src.database.models import User, UserRole
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()


class UserCreate(BaseModel):
    """User registration model."""
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.PLAYER


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model."""
    username: str | None = None


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user. Only PLAYER and VIEWER roles allowed for self-registration."""
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Restrict self-registration to PLAYER or VIEWER roles only
    # ADMIN and DESIGNER roles must be assigned by an existing admin
    if user_data.role not in [UserRole.PLAYER, UserRole.VIEWER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PLAYER and VIEWER roles can be self-assigned. Contact an admin for elevated roles."
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout():
    """Logout endpoint (client should discard token)."""
    # JWT tokens are stateless, so logout is handled client-side
    # by discarding the token
    return {"message": "Successfully logged out"}


@router.post("/create-admin")
async def create_admin_endpoint(
    username: str,
    email: str,
    password: str,
    secret_token: str,
    db: Session = Depends(get_db)
):
    """
    One-time admin creation endpoint.
    Protected by SECRET_KEY - use your Railway SECRET_KEY as the secret_token.
    This endpoint should be removed or disabled after creating the first admin.
    """
    import os
    
    # Verify secret token matches SECRET_KEY
    expected_secret = os.getenv("SECRET_KEY")
    if not expected_secret or secret_token != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret token"
        )
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin user already exists. Use the admin panel to create additional admins."
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return {
        "message": "Admin user created successfully",
        "username": admin.username,
        "email": admin.email,
        "role": admin.role.value
    }
