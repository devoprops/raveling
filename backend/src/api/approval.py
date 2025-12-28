"""Approval API routes for moving configs from GitHub to production database."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.sql import func
from pydantic import BaseModel
import json

from src.database.database import get_db
from src.database.models import User, Config, ApprovedConfig, ConfigType
from src.core.security import get_current_active_user, require_role, UserRole
from src.core.github_storage import github_storage

router = APIRouter()


class ApprovedConfigResponse(BaseModel):
    """Approved config response schema."""
    id: int
    name: str
    config_type: ConfigType
    config_content: dict
    description: str | None
    tags: str | None
    github_path: str | None
    approved_at: str
    updated_at: str | None

    class Config:
        from_attributes = True


@router.post("/items/{config_id}/approve", response_model=ApprovedConfigResponse)
async def approve_item(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Approve an item config and move it to production database."""
    return await _approve_config(config_id, ConfigType.ITEM, db, current_user)


@router.post("/skills/{config_id}/approve", response_model=ApprovedConfigResponse)
async def approve_skill(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Approve a skill config and move it to production database."""
    return await _approve_config(config_id, ConfigType.SKILL, db, current_user)


@router.post("/characters/{config_id}/approve", response_model=ApprovedConfigResponse)
async def approve_character(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Approve a character config and move it to production database."""
    return await _approve_config(config_id, ConfigType.CHARACTER, db, current_user)


async def _approve_config(
    config_id: int,
    config_type: ConfigType,
    db: Session,
    current_user: User
) -> ApprovedConfigResponse:
    """Internal function to approve a config."""
    # Get design config
    design_config = db.query(Config).filter(
        Config.id == config_id,
        Config.config_type == config_type
    ).first()
    
    if not design_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{config_type.value.capitalize()} config not found"
        )
    
    # Load content from GitHub
    try:
        content = github_storage.load_config(config_type.value, design_config.name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config file not found in GitHub"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load config from GitHub: {str(e)}"
        )
    
    # Convert content to JSON string for storage
    config_content_json = json.dumps(content)
    
    # Check if approved config already exists (for re-approval)
    existing_approved = db.query(ApprovedConfig).filter(
        ApprovedConfig.name == design_config.name,
        ApprovedConfig.config_type == config_type
    ).first()
    
    if existing_approved:
        # Update existing approved config
        existing_approved.config_content = config_content_json
        existing_approved.github_path = design_config.github_path
        existing_approved.github_sha = design_config.github_sha
        existing_approved.source_config_id = design_config.id
        existing_approved.description = design_config.description
        existing_approved.tags = design_config.tags
        existing_approved.approved_by_id = current_user.id
        db.commit()
        db.refresh(existing_approved)
        
        # Update design config approval status
        design_config.is_approved = True
        design_config.approved_at = func.now()
        design_config.approved_by_id = current_user.id
        db.commit()
        
        return ApprovedConfigResponse(
            id=existing_approved.id,
            name=existing_approved.name,
            config_type=existing_approved.config_type,
            config_content=content,
            description=existing_approved.description,
            tags=existing_approved.tags,
            github_path=existing_approved.github_path,
            approved_at=existing_approved.approved_at.isoformat() if existing_approved.approved_at else "",
            updated_at=existing_approved.updated_at.isoformat() if existing_approved.updated_at else None
        )
    else:
        # Create new approved config
        approved_config = ApprovedConfig(
            name=design_config.name,
            config_type=config_type,
            config_content=config_content_json,
            github_path=design_config.github_path,
            github_sha=design_config.github_sha,
            source_config_id=design_config.id,
            description=design_config.description,
            tags=design_config.tags,
            approved_by_id=current_user.id
        )
        
        db.add(approved_config)
        
        # Update design config approval status
        design_config.is_approved = True
        design_config.approved_at = func.now()
        design_config.approved_by_id = current_user.id
        
        db.commit()
        db.refresh(approved_config)
        
        return ApprovedConfigResponse(
            id=approved_config.id,
            name=approved_config.name,
            config_type=approved_config.config_type,
            config_content=content,
            description=approved_config.description,
            tags=approved_config.tags,
            github_path=approved_config.github_path,
            approved_at=approved_config.approved_at.isoformat() if approved_config.approved_at else "",
            updated_at=approved_config.updated_at.isoformat() if approved_config.updated_at else None
        )


@router.get("/items/approved", response_model=List[ApprovedConfigResponse])
async def list_approved_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all approved item configs."""
    return await _list_approved_configs(ConfigType.ITEM, skip, limit, db)


@router.get("/skills/approved", response_model=List[ApprovedConfigResponse])
async def list_approved_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all approved skill configs."""
    return await _list_approved_configs(ConfigType.SKILL, skip, limit, db)


@router.get("/characters/approved", response_model=List[ApprovedConfigResponse])
async def list_approved_characters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all approved character configs."""
    return await _list_approved_configs(ConfigType.CHARACTER, skip, limit, db)


async def _list_approved_configs(
    config_type: ConfigType,
    skip: int,
    limit: int,
    db: Session
) -> List[ApprovedConfigResponse]:
    """Internal function to list approved configs."""
    approved_configs = db.query(ApprovedConfig).filter(
        ApprovedConfig.config_type == config_type
    ).offset(skip).limit(limit).all()
    
    result = []
    for approved_config in approved_configs:
        content = json.loads(approved_config.config_content)
        result.append(ApprovedConfigResponse(
            id=approved_config.id,
            name=approved_config.name,
            config_type=approved_config.config_type,
            config_content=content,
            description=approved_config.description,
            tags=approved_config.tags,
            github_path=approved_config.github_path,
            approved_at=approved_config.approved_at.isoformat() if approved_config.approved_at else "",
            updated_at=approved_config.updated_at.isoformat() if approved_config.updated_at else None
        ))
    
    return result


@router.get("/items/approved/{name}", response_model=ApprovedConfigResponse)
async def get_approved_item(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get approved item config by name (for game use)."""
    return await _get_approved_config(name, ConfigType.ITEM, db)


@router.get("/skills/approved/{name}", response_model=ApprovedConfigResponse)
async def get_approved_skill(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get approved skill config by name (for game use)."""
    return await _get_approved_config(name, ConfigType.SKILL, db)


@router.get("/characters/approved/{name}", response_model=ApprovedConfigResponse)
async def get_approved_character(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get approved character config by name (for game use)."""
    return await _get_approved_config(name, ConfigType.CHARACTER, db)


async def _get_approved_config(
    name: str,
    config_type: ConfigType,
    db: Session
) -> ApprovedConfigResponse:
    """Internal function to get approved config."""
    approved_config = db.query(ApprovedConfig).filter(
        ApprovedConfig.name == name,
        ApprovedConfig.config_type == config_type
    ).first()
    
    if not approved_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approved {config_type.value} config '{name}' not found"
        )
    
    content = json.loads(approved_config.config_content)
    
    return ApprovedConfigResponse(
        id=approved_config.id,
        name=approved_config.name,
        config_type=approved_config.config_type,
        config_content=content,
        description=approved_config.description,
        tags=approved_config.tags,
        github_path=approved_config.github_path,
        approved_at=approved_config.approved_at.isoformat() if approved_config.approved_at else "",
        updated_at=approved_config.updated_at.isoformat() if approved_config.updated_at else None
    )

