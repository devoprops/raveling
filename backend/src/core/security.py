"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.database.models import User, UserRole

# Password hashing
# Use bcrypt with explicit configuration to avoid version check issues
# Passlib has issues detecting bcrypt 4.x version, so we configure it explicitly
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__ident="2b",  # Use bcrypt 2b identifier (compatible with bcrypt 4.x)
        bcrypt__rounds=12,  # Explicit rounds to avoid detection issues
    )

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# JWT settings
import os
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash. Supports both passlib and direct bcrypt hashes."""
    try:
        # Try passlib first (works for passlib-generated hashes)
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError, AttributeError):
        # If passlib fails, try direct bcrypt verification (for direct bcrypt hashes)
        try:
            import bcrypt
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except (ImportError, ValueError, TypeError):
            # If both fail, return False
            return False


def get_password_hash(password: str) -> str:
    """Hash a password. Bcrypt has a 72-byte limit, so we truncate if necessary."""
    # Bcrypt has a 72-byte limit, encode to bytes and truncate if needed
    password_bytes = password.encode('utf-8')
    original_length = len(password_bytes)
    
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        # Try to decode back, but if it's in the middle of a multi-byte character, 
        # we'll get a valid string up to that point
        try:
            password = password_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # If we're in the middle of a multi-byte character, decode with error handling
            password = password_bytes.decode('utf-8', errors='ignore')
    
    try:
        return pwd_context.hash(password)
    except (ValueError, TypeError) as e:
        error_msg = str(e)
        # Check if it's the 72-byte error (which shouldn't happen for short passwords)
        if "72" in error_msg or "longer" in error_msg.lower():
            # Passlib might be having issues with bcrypt. Try using bcrypt directly as fallback
            try:
                import bcrypt
                # Use bcrypt directly - encode password to bytes
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
                salt = bcrypt.gensalt(rounds=12)
                hashed = bcrypt.hashpw(password_bytes, salt)
                # Return as string (bcrypt returns bytes)
                return hashed.decode('utf-8')
            except ImportError:
                raise ValueError(
                    f"Password hashing failed and bcrypt module not available. "
                    f"Error: {error_msg}. Password length: {original_length} bytes ({len(password)} chars)."
                )
            except Exception as bcrypt_error:
                raise ValueError(
                    f"Password hashing failed with both passlib and direct bcrypt. "
                    f"Passlib error: {error_msg}. Bcrypt error: {bcrypt_error}. "
                    f"Password length: {original_length} bytes ({len(password)} chars)."
                )
        # If there's still an error, provide more context
        raise ValueError(f"Failed to hash password: {error_msg}. Password length: {original_length} bytes")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(*allowed_roles: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
