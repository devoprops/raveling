"""Spells API routes."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.database import get_db
from src.database.models import User
from src.core.security import get_current_active_user, require_role, UserRole
from src.core.github_storage import github_storage

router = APIRouter()


@router.get("/list-configs")
async def list_spell_configs(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    List all spell configurations from GitHub storage.
    
    Returns:
        List of spell config names
    """
    try:
        config_names = github_storage.list_configs("spell")
        return {"configs": config_names}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list spell configs: {str(e)}"
        )


@router.get("/load-config/{spell_name}")
async def load_spell_config(
    spell_name: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Load a spell configuration from GitHub storage.
    
    Args:
        spell_name: Name of the spell config to load
        
    Returns:
        Spell configuration dictionary
    """
    try:
        config = github_storage.load_config("spell", spell_name)
        return {"spell_config": config}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spell config '{spell_name}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load spell config: {str(e)}"
        )


class SpellConfigRequest(BaseModel):
    """Request schema for saving spell config."""
    spell_config: Dict[str, Any]


@router.post("/save-config")
async def save_spell_config(
    request: SpellConfigRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Save a spell configuration to GitHub storage.
    
    Args:
        request: Contains spell_config dictionary
        
    Returns:
        Dictionary with commit_sha and file_path
    """
    try:
        spell_name = request.spell_config.get("name", "unnamed_spell")
        if not spell_name or spell_name == "unnamed_spell":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Spell name is required"
            )
        
        # Save to GitHub
        try:
            commit_sha = github_storage.save_config(
                config_type="spell",
                name=spell_name,
                content=request.spell_config,
                commit_message=f"Save spell config: {spell_name}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save spell config to GitHub: {str(e)}"
            )
        
        return {
            "commit_sha": commit_sha,
            "file_path": github_storage.get_file_path("spell", spell_name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save spell config: {str(e)}"
        )
