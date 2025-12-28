"""Authentication schemas."""

from pydantic import BaseModel, EmailStr
from typing import Optional
from src.database.models import UserRole


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema."""
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.PLAYER


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str

