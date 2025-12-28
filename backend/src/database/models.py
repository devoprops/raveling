"""Database models for Raveling MUD."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from src.database.database import Base


class UserRole(str, enum.Enum):
    """User roles for access control."""
    ADMIN = "admin"
    DESIGNER = "designer"
    PLAYER = "player"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.PLAYER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    configs = relationship("Config", back_populates="owner", foreign_keys="[Config.owner_id]")


class ConfigType(str, enum.Enum):
    """Types of configuration files."""
    ITEM = "item"
    SKILL = "skill"
    CHARACTER = "character"


class Config(Base):
    """Design configuration file storage (metadata for GitHub-stored configs)."""
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    config_type = Column(SQLEnum(ConfigType), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # GitHub storage info
    github_path = Column(String, nullable=True)  # Path in GitHub repo
    github_sha = Column(String, nullable=True)  # Last commit SHA
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags
    
    # Approval status
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="configs", foreign_keys=[owner_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])


class ApprovedConfig(Base):
    """Approved configuration for production use (stored in database)."""
    __tablename__ = "approved_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    config_type = Column(SQLEnum(ConfigType), nullable=False, index=True)
    
    # Full config content stored in database
    config_content = Column(Text, nullable=False)  # JSON/YAML string
    
    # Source info
    source_config_id = Column(Integer, ForeignKey("configs.id"), nullable=True)  # Link to design config
    github_path = Column(String, nullable=True)  # Original GitHub path
    github_sha = Column(String, nullable=True)  # GitHub commit SHA when approved
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    
    # Approval info
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    approved_by = relationship("User")
