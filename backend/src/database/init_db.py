"""Initialize database tables."""

from src.database.database import engine, Base
from src.database.models import User, Config, ApprovedConfig

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()

