"""FastAPI backend for Raveling MUD."""

from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file (for local development only)
# Railway and other platforms inject env vars directly, so .env is optional
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded .env file from: {env_path}")
else:
    print("No .env file found - using environment variables directly (production mode)")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth, items, skills, characters, approval, users, effectors

# Initialize database tables on startup
try:
    from src.database.init_db import init_db
    init_db()
    print("✅ Database tables initialized")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")
    # Don't crash - tables might already exist or connection might not be ready yet

app = FastAPI(
    title="Raveling MUD API",
    description="Backend API for Raveling MUD Designer and Game",
    version="0.1.0",
)

# CORS middleware - configure allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://raveling.devocosm.com",
        "http://localhost:3000",  # Frontend dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(approval.router, prefix="/api/approval", tags=["approval"])
app.include_router(effectors.router, prefix="/api/effectors", tags=["effectors"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Raveling MUD API", "version": "0.1.0"}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

