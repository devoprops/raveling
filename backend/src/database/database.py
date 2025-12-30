"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment, default to SQLite for local dev
# Handle empty strings - if DATABASE_URL is empty, use SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./raveling.db"

# For PostgreSQL on Railway, DATABASE_URL will be provided
# Format: postgresql://user:password@host:port/database
# For SQLite (local dev): sqlite:///./raveling.db

if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL connection
    engine = create_engine(DATABASE_URL)
else:
    # SQLite connection (for local development)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
