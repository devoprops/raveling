"""Items API routes."""

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
    content: dict  # Loaded from GitHub

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ConfigResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all item configs."""
    configs = db.query(Config).filter(
        Config.config_type == ConfigType.ITEM,
        Config.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Load content from GitHub for each config
    result = []
    for config in configs:
        try:
            content = github_storage.load_config("item", config.name)
        except (FileNotFoundError, RuntimeError):
            # Config file doesn't exist in GitHub, skip it or use empty dict
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


@router.get("/{item_id}", response_model=ConfigResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get item config by ID."""
    config = db.query(Config).filter(
        Config.id == item_id,
        Config.config_type == ConfigType.ITEM,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        content = github_storage.load_config("item", config.name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item config file not found in GitHub"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load item from GitHub: {str(e)}"
        )
    
    return ConfigResponse(
        id=config.id,
        name=config.name,
        config_type=config.config_type,
        description=config.description,
        tags=config.tags,
        github_path=config.github_path,
        created_at=config.created_at.isoformat() if config.created_at else "",
        updated_at=config.updated_at.isoformat() if config.updated_at else "",
        content=content
    )


@router.post("/", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Create new item config."""
    # Check if item with same name exists
    existing = db.query(Config).filter(
        Config.name == item_data.name,
        Config.config_type == ConfigType.ITEM,
        Config.owner_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item with this name already exists"
        )
    
    # Save to GitHub first
    try:
        github_sha = github_storage.save_config(
            config_type="item",
            name=item_data.name,
            content=item_data.content
        )
        github_path = github_storage.get_file_path("item", item_data.name)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save item to GitHub: {str(e)}"
        )
    
    # Save metadata to database
    config = Config(
        name=item_data.name,
        config_type=ConfigType.ITEM,
        owner_id=current_user.id,
        description=item_data.description,
        tags=item_data.tags,
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
        is_approved=config.is_approved,
        approved_at=config.approved_at.isoformat() if config.approved_at else None,
        created_at=config.created_at.isoformat() if config.created_at else "",
        updated_at=config.updated_at.isoformat() if config.updated_at else "",
        content=item_data.content
    )


@router.put("/{item_id}", response_model=ConfigResponse)
async def update_item(
    item_id: int,
    item_data: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Update an item config."""
    config = db.query(Config).filter(
        Config.id == item_id,
        Config.config_type == ConfigType.ITEM,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update content in GitHub if provided
    if item_data.content is not None:
        try:
            github_sha = github_storage.save_config(
                config_type="item",
                name=item_data.name or config.name,
                content=item_data.content
            )
            config.github_sha = github_sha
            if item_data.name:
                config.github_path = github_storage.get_file_path("item", item_data.name)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update item in GitHub: {str(e)}"
            )
    
    # Update metadata
    if item_data.name is not None:
        config.name = item_data.name
    if item_data.description is not None:
        config.description = item_data.description
    if item_data.tags is not None:
        config.tags = item_data.tags
    
    db.commit()
    db.refresh(config)
    
    # Load updated content
    try:
        content = github_storage.load_config("item", config.name)
    except (FileNotFoundError, RuntimeError):
        # Fallback to provided content if GitHub load fails
        content = item_data.content or {}
    
    return ConfigResponse(
        id=config.id,
        name=config.name,
        config_type=config.config_type,
        description=config.description,
        tags=config.tags,
        github_path=config.github_path,
        created_at=config.created_at.isoformat() if config.created_at else "",
        updated_at=config.updated_at.isoformat() if config.updated_at else "",
        content=content
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Delete an item config."""
    config = db.query(Config).filter(
        Config.id == item_id,
        Config.config_type == ConfigType.ITEM,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Delete from GitHub
    try:
        github_storage.delete_config("item", config.name)
    except FileNotFoundError:
        # File already deleted, continue
        pass
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item from GitHub: {str(e)}"
        )
    
    # Delete from database
    db.delete(config)
    db.commit()
    
    return None
