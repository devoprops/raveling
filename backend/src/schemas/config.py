"""Configuration schemas."""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from src.database.models import ConfigType


class ConfigCreate(BaseModel):
    """Config creation schema."""
    name: str
    config_type: ConfigType
    subtype: Optional[str] = None
    content: Dict[str, Any]


class ConfigUpdate(BaseModel):
    """Config update schema."""
    name: Optional[str] = None
    subtype: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


class ConfigResponse(BaseModel):
    """Config response schema."""
    id: int
    name: str
    config_type: ConfigType
    subtype: Optional[str]
    content: Dict[str, Any]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

