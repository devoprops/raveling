"""Characters API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.database import get_db
from src.database.models import User, Config, ConfigType
from src.core.security import get_current_active_user, require_role, UserRole
from src.core.github_storage import github_storage

router = APIRouter()


class ConfigCreate(BaseModel):
    """Config creation schema."""
    name: str
    content: dict
    description: Optional[str] = None
    tags: Optional[str] = None


class ConfigUpdate(BaseModel):
    """Config update schema."""
    name: Optional[str] = None
    content: Optional[dict] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class ConfigResponse(BaseModel):
    """Design config response schema (from GitHub)."""
    id: int
    name: str
    config_type: ConfigType
    description: Optional[str]
    tags: Optional[str]
    github_path: Optional[str]
    is_approved: bool
    approved_at: Optional[str]
    created_at: str
    updated_at: str
    content: dict

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ConfigResponse])
async def list_characters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all character configs."""
    configs = db.query(Config).filter(
        Config.config_type == ConfigType.CHARACTER,
        Config.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    result = []
    for config in configs:
        try:
            content = github_storage.load_config("character", config.name)
        except (FileNotFoundError, RuntimeError):
            # Config file doesn't exist in GitHub, skip it
            continue
        result.append(ConfigResponse(
            id=config.id,
            name=config.name,
            config_type=config.config_type,
            description=config.description,
            tags=config.tags,
            github_path=config.github_path,
            is_approved=config.is_approved,
            approved_at=config.approved_at.isoformat() if config.approved_at else None,
            created_at=config.created_at.isoformat() if config.created_at else "",
            updated_at=config.updated_at.isoformat() if config.updated_at else "",
            content=content
        ))
    
    return result


@router.get("/{character_id}", response_model=ConfigResponse)
async def get_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get character config by ID."""
    config = db.query(Config).filter(
        Config.id == character_id,
        Config.config_type == ConfigType.CHARACTER,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    try:
        content = github_storage.load_config("character", config.name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character config file not found in GitHub"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load character from GitHub: {str(e)}"
        )
    
    return ConfigResponse(
        id=config.id,
        name=config.name,
        config_type=config.config_type,
        description=config.description,
        tags=config.tags,
        github_path=config.github_path,
        is_approved=config.is_approved,
        approved_at=config.approved_at.isoformat() if config.approved_at else None,
        created_at=config.created_at.isoformat() if config.created_at else "",
        updated_at=config.updated_at.isoformat() if config.updated_at else "",
        content=content
    )


@router.post("/", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_data: ConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new character config."""
    existing = db.query(Config).filter(
        Config.name == character_data.name,
        Config.config_type == ConfigType.CHARACTER,
        Config.owner_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character with this name already exists"
        )
    
    try:
        github_sha = github_storage.save_config(
            config_type="character",
            name=character_data.name,
            content=character_data.content
        )
        github_path = github_storage.get_file_path("character", character_data.name)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save character to GitHub: {str(e)}"
        )
    
    config = Config(
        name=character_data.name,
        config_type=ConfigType.CHARACTER,
        owner_id=current_user.id,
        description=character_data.description,
        tags=character_data.tags,
        github_path=github_path,
        github_sha=github_sha
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return ConfigResponse(
        id=config.id,
        name=config.name,
        config_type=config.config_type,
        description=config.description,
        tags=config.tags,
        github_path=config.github_path,
        created_at=config.created_at.isoformat() if config.created_at else "",
        updated_at=config.updated_at.isoformat() if config.updated_at else "",
        content=character_data.content
    )


@router.put("/{character_id}", response_model=ConfigResponse)
async def update_character(
    character_id: int,
    character_data: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a character config."""
    config = db.query(Config).filter(
        Config.id == character_id,
        Config.config_type == ConfigType.CHARACTER,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    if character_data.content is not None:
        try:
            github_sha = github_storage.save_config(
                config_type="character",
                name=character_data.name or config.name,
                content=character_data.content
            )
            config.github_sha = github_sha
            if character_data.name:
                config.github_path = github_storage.get_file_path("character", character_data.name)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update character in GitHub: {str(e)}"
            )
    
    if character_data.name is not None:
        config.name = character_data.name
    if character_data.description is not None:
        config.description = character_data.description
    if character_data.tags is not None:
        config.tags = character_data.tags
    
    db.commit()
    db.refresh(config)
    
    try:
        content = github_storage.load_config("character", config.name)
    except (FileNotFoundError, RuntimeError):
        # Fallback to provided content if GitHub load fails
        content = character_data.content or {}
    
    return ConfigResponse(
        id=config.id,
        name=config.name,
        config_type=config.config_type,
        description=config.description,
        tags=config.tags,
        github_path=config.github_path,
        is_approved=config.is_approved,
        approved_at=config.approved_at.isoformat() if config.approved_at else None,
        created_at=config.created_at.isoformat() if config.created_at else "",
        updated_at=config.updated_at.isoformat() if config.updated_at else "",
        content=content
    )


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a character config."""
    config = db.query(Config).filter(
        Config.id == character_id,
        Config.config_type == ConfigType.CHARACTER,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    try:
        github_storage.delete_config("character", config.name)
    except FileNotFoundError:
        # File already deleted, continue
        pass
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete character from GitHub: {str(e)}"
        )
    
    db.delete(config)
    db.commit()
    
    return None
