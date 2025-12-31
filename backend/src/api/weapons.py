"""Weapons API routes for analysis and thumbnail upload."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.database import get_db
from src.database.models import User
from src.core.security import get_current_active_user, require_role, UserRole
from src.core.github_storage import github_storage
from src.utils.weapon_analysis import simulate_damage

router = APIRouter()


class DamageAnalysisRequest(BaseModel):
    """Request schema for damage analysis."""
    weapon_config: Dict[str, Any]
    num_strikes: int = 100


class DamageAnalysisResponse(BaseModel):
    """Response schema for damage analysis."""
    strikes: list[int]
    cumulative_damage: list[float]
    damage_values: list[float]
    damage_per_strike: list[float]
    effector_breakdown: Optional[Dict[str, list[float]]] = None
    effector_cumulative: Optional[Dict[str, list[float]]] = None
    style_breakdown: Optional[Dict[str, list[float]]] = None
    style_cumulative: Optional[Dict[str, list[float]]] = None
    min_damage: float
    max_damage: float


@router.post("/analyze-damage", response_model=DamageAnalysisResponse)
async def analyze_damage(
    request: DamageAnalysisRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Simulate weapon damage over N strikes.
    
    Args:
        request: Contains weapon_config and num_strikes
        
    Returns:
        Analysis results with strikes, cumulative damage, damage values, min/max
    """
    try:
        # Validate num_strikes
        if request.num_strikes < 1 or request.num_strikes > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="num_strikes must be between 1 and 10000"
            )
        
        # Run simulation
        results = simulate_damage(request.weapon_config, request.num_strikes)
        
        return DamageAnalysisResponse(**results)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze damage: {str(e)}"
        )


class WeaponConfigRequest(BaseModel):
    """Request schema for saving weapon config."""
    weapon_config: Dict[str, Any]


@router.post("/save-config")
async def save_weapon_config(
    request: WeaponConfigRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Save a weapon configuration to GitHub storage.
    
    Args:
        request: Contains weapon_config dictionary
        
    Returns:
        Dictionary with commit_sha and file_path
    """
    try:
        weapon_name = request.weapon_config.get("name", "unnamed_weapon")
        if not weapon_name or weapon_name == "unnamed_weapon":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weapon name is required"
            )
        
        # Save to GitHub
        try:
            commit_sha = github_storage.save_config(
                config_type="weapon",
                name=weapon_name,
                content=request.weapon_config,
                commit_message=f"Save weapon config: {weapon_name}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save weapon config to GitHub: {str(e)}"
            )
        
        return {
            "commit_sha": commit_sha,
            "file_path": github_storage.get_file_path("weapon", weapon_name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save weapon config: {str(e)}"
        )


@router.post("/upload-thumbnail")
async def upload_thumbnail(
    item_name: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
):
    """
    Upload a thumbnail image for an item.
    
    Args:
        item_name: Name of the item (used for filename)
        file: Image file (PNG, JPG, etc.)
        
    Returns:
        Dictionary with thumbnail_path
    """
    try:
        # Validate file type
        allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
        file_ext = None
        for ext in allowed_extensions:
            if file.filename.lower().endswith(ext):
                file_ext = ext
                break
        
        if not file_ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size (max 2MB)
        max_size = 2 * 1024 * 1024  # 2MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 2MB limit"
            )
        
        # Sanitize item name for filename
        safe_name = "".join(c for c in item_name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            safe_name = "item"
        
        # Construct file path in GitHub
        file_path = f"thumbnails/items/{safe_name}{file_ext}"
        
        # Save to GitHub
        try:
            commit_sha = github_storage.save_file(
                file_path=file_path,
                content=content,
                commit_message=f"Upload thumbnail for item: {item_name}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload thumbnail to GitHub: {str(e)}"
            )
        
        return {
            "thumbnail_path": file_path,
            "commit_sha": commit_sha
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload thumbnail: {str(e)}"
        )

