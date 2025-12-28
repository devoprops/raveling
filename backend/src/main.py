"""FastAPI backend for Raveling MUD."""

from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# Find .env file relative to this file's location
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Debug: Check if token is loaded (remove after testing)
print(f"GITHUB_TOKEN loaded: {bool(os.getenv('GITHUB_TOKEN'))}")
print(f"GITHUB_REPO: {os.getenv('GITHUB_REPO')}")
print(f"Looking for .env at: {env_path}")
print(f".env file exists: {env_path.exists()}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth, items, skills, characters, approval
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
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(approval.router, prefix="/api/approval", tags=["approval"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Raveling MUD API", "version": "0.1.0"}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

