"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Raveling MUD API"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "https://raveling.devocosm.com",
        "http://localhost:3000",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./raveling.db"
    
    # GitHub Storage
    GITHUB_TOKEN: str = ""  # GitHub personal access token
    GITHUB_REPO_OWNER: str = ""  # Repository owner (username or org)
    GITHUB_REPO: str = ""  # Repository name
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

