"""Skills API routes."""

from typing import List, Optional, Dict, Any
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
async def list_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all skill configs."""
    configs = db.query(Config).filter(
        Config.config_type == ConfigType.SKILL,
        Config.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    result = []
    for config in configs:
        try:
            content = github_storage.load_config("skill", config.name)
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


@router.get("/{skill_id}", response_model=ConfigResponse)
async def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get skill config by ID."""
    config = db.query(Config).filter(
        Config.id == skill_id,
        Config.config_type == ConfigType.SKILL,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    try:
        content = github_storage.load_config("skill", config.name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill config file not found in GitHub"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load skill from GitHub: {str(e)}"
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
async def create_skill(
    skill_data: ConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Create new skill config."""
    existing = db.query(Config).filter(
        Config.name == skill_data.name,
        Config.config_type == ConfigType.SKILL,
        Config.owner_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill with this name already exists"
        )
    
    try:
        github_sha = github_storage.save_config(
            config_type="skill",
            name=skill_data.name,
            content=skill_data.content
        )
        github_path = github_storage.get_file_path("skill", skill_data.name)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save skill to GitHub: {str(e)}"
        )
    
    config = Config(
        name=skill_data.name,
        config_type=ConfigType.SKILL,
        owner_id=current_user.id,
        description=skill_data.description,
        tags=skill_data.tags,
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
        content=skill_data.content
    )


@router.put("/{skill_id}", response_model=ConfigResponse)
async def update_skill(
    skill_id: int,
    skill_data: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Update a skill config."""
    config = db.query(Config).filter(
        Config.id == skill_id,
        Config.config_type == ConfigType.SKILL,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if skill_data.content is not None:
        try:
            github_sha = github_storage.save_config(
                config_type="skill",
                name=skill_data.name or config.name,
                content=skill_data.content
            )
            config.github_sha = github_sha
            if skill_data.name:
                config.github_path = github_storage.get_file_path("skill", skill_data.name)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update skill in GitHub: {str(e)}"
            )
    
    if skill_data.name is not None:
        config.name = skill_data.name
    if skill_data.description is not None:
        config.description = skill_data.description
    if skill_data.tags is not None:
        config.tags = skill_data.tags
    
    db.commit()
    db.refresh(config)
    
    try:
        content = github_storage.load_config("skill", config.name)
    except (FileNotFoundError, RuntimeError):
        # Fallback to provided content if GitHub load fails
        content = skill_data.content or {}
    
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


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DESIGNER, UserRole.ADMIN))
):
    """Delete a skill config."""
    config = db.query(Config).filter(
        Config.id == skill_id,
        Config.config_type == ConfigType.SKILL,
        Config.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    try:
        github_storage.delete_config("skill", config.name)
    except FileNotFoundError:
        # File already deleted, continue
        pass
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete skill from GitHub: {str(e)}"
        )
    
    db.delete(config)
    db.commit()
    
    return None


@router.get("/list-configs")
async def list_skill_configs(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    List all skill configurations from GitHub storage.
    
    Returns:
        List of skill config names
    """
    try:
        config_names = github_storage.list_configs("skill")
        return {"configs": config_names}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list skill configs: {str(e)}"
        )


@router.get("/load-config/{skill_name}")
async def load_skill_config(
    skill_name: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Load a skill configuration from GitHub storage.
    
    Args:
        skill_name: Name of the skill config to load
        
    Returns:
        Skill configuration dictionary
    """
    try:
        config = github_storage.load_config("skill", skill_name)
        return {"skill_config": config}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill config '{skill_name}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load skill config: {str(e)}"
        )


class SkillConfigRequest(BaseModel):
    """Request schema for saving skill config."""
    skill_config: Dict[str, Any]


@router.post("/save-config")
async def save_skill_config(
    request: SkillConfigRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Save a skill configuration to GitHub storage.
    
    Args:
        skill_config: Skill configuration dictionary
        
    Returns:
        Dictionary with commit_sha and file_path
    """
    try:
        skill_name = request.skill_config.get("name", "unnamed_skill")
        if not skill_name or skill_name == "unnamed_skill":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill name is required"
            )
        
        # Save to GitHub
        try:
            commit_sha = github_storage.save_config(
                config_type="skill",
                name=skill_name,
                content=request.skill_config,
                commit_message=f"Save skill config: {skill_name}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save skill config to GitHub: {str(e)}"
            )
        
        return {
            "commit_sha": commit_sha,
            "file_path": github_storage.get_file_path("skill", skill_name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save skill config: {str(e)}"
        )
