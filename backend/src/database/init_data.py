"""Initialize database with default data."""

from src.database.database import SessionLocal
from src.database.models import User, UserRole
from src.core.security import get_password_hash


def create_default_admin():
    """Create a default admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@raveling.local",
                hashed_password=get_password_hash("admin123"),  # Change this!
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.commit()
            print("Default admin user created: username='admin', password='admin123'")
            print("⚠️  IMPORTANT: Change the admin password immediately!")
        else:
            print("Admin user already exists")
    finally:
        db.close()


if __name__ == "__main__":
    from src.database.database import init_db
    init_db()
    create_default_admin()

