#!/usr/bin/env python3
"""Script to create an admin user with custom credentials."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import SessionLocal
from src.database.init_db import init_db
from src.database.models import User, UserRole
from src.core.security import get_password_hash


def delete_user(username: str):
    """Delete a user by username."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            db.delete(user)
            db.commit()
            print(f"✅ Deleted user '{username}'")
            return True
        else:
            print(f"⚠️  User '{username}' not found")
            return False
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting user: {e}")
        return False
    finally:
        db.close()


def create_admin(username: str, email: str, password: str, delete_existing: bool = False):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if admin with this username exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            if delete_existing:
                print(f"⚠️  User '{username}' already exists. Deleting...")
                db.delete(existing_user)
                db.commit()
            else:
                print(f"❌ User '{username}' already exists! Use --delete-existing to replace it.")
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
    parser.add_argument("--delete-existing", action="store_true", help="Delete existing user with same username first")
    
    args = parser.parse_args()
    
    if args.init_db:
        print("Initializing database...")
        init_db()
    
    create_admin(args.username, args.email, args.password, args.delete_existing)

