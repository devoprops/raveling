#!/usr/bin/env python3
"""Script to create an admin user with custom credentials."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import SessionLocal, init_db
from src.database.models import User, UserRole
from src.core.security import get_password_hash


def create_admin(username: str, email: str, password: str):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if admin with this username exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists!")
            return False
        
        # Check if email is already taken
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"❌ Email '{email}' is already registered!")
            return False
        
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
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: ADMIN")
        print(f"\n⚠️  Keep your password secure!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user for Raveling")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables first")
    
    args = parser.parse_args()
    
    if args.init_db:
        print("Initializing database...")
        init_db()
    
    create_admin(args.username, args.email, args.password)

