"""EffectStyle API routes for managing effect styles."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.database import get_db
from src.database.models import User, EffectStyle
from src.core.security import get_current_active_user, require_role, UserRole

router = APIRouter()


class EffectStyleConfig(BaseModel):
    """EffectStyle configuration model."""
    name: str
    style_type: str
    subtype: str
    description: Optional[str] = ""
    process_verb: Optional[str] = ""
    execution_probability: float = 1.0
    effector: Optional[Dict[str, Any]] = None  # Single effector (backwards compat)
    effectors: Optional[List[Dict[str, Any]]] = None  # Multiple effectors (new)
    style_attributes: Optional[Dict[str, Any]] = None  # Type-specific attributes


class EffectStyleResponse(BaseModel):
    """EffectStyle response model."""
    id: int
    name: str
    style_type: str
    subtype: str
    description: Optional[str]
    process_verb: Optional[str]
    execution_probability: float
    effector_config: Dict[str, Any]  # Can be single effector or list
    style_attributes: Optional[Dict[str, Any]] = None
    created_by_id: int
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class EffectStyleTreeResponse(BaseModel):
    """Tree structure response for effect styles."""
    Physical: Dict[str, List[EffectStyleResponse]]
    Spell: Dict[str, List[EffectStyleResponse]]
    Buff: Dict[str, List[EffectStyleResponse]]
    Debuff: Dict[str, List[EffectStyleResponse]]
    Regen: Dict[str, List[EffectStyleResponse]]
    Process: Dict[str, List[EffectStyleResponse]]


@router.get("/", response_model=EffectStyleTreeResponse)
async def list_effect_styles(
    style_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all effect styles organized by type in tree structure.
    
    Returns tree structure: {type: {pre_designed: [...], custom: {...}}}
    """
    query = db.query(EffectStyle)
    
    if style_type:
        query = query.filter(EffectStyle.style_type == style_type)
    
    all_styles = query.all()
    
    # Organize by type
    tree: Dict[str, Dict[str, List[EffectStyleResponse]]] = {
        "Physical": {"pre_designed": [], "custom": []},
        "Spell": {"pre_designed": [], "custom": []},
        "Buff": {"pre_designed": [], "custom": []},
        "Debuff": {"pre_designed": [], "custom": []},
        "Regen": {"pre_designed": [], "custom": []},
        "Process": {"pre_designed": [], "custom": []},
    }
    
    for style in all_styles:
        style_response = EffectStyleResponse(
            id=style.id,
            name=style.name,
            style_type=style.style_type,
            subtype=style.subtype,
            description=style.description,
            process_verb=style.process_verb,
            execution_probability=style.execution_probability,
            effector_config=style.effector_config,
            style_attributes=style.style_attributes,
            created_by_id=style.created_by_id,
            created_at=style.created_at.isoformat() if style.created_at else "",
            updated_at=style.updated_at.isoformat() if style.updated_at else None,
        )
        
        # For now, all styles are "pre_designed" (saved to library)
        # "custom" would be for inline styles that aren't saved
        if style.style_type in tree:
            tree[style.style_type]["pre_designed"].append(style_response)
    
    return tree


@router.get("/{style_id}", response_model=EffectStyleResponse)
async def get_effect_style(
    style_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific effect style by ID."""
    style = db.query(EffectStyle).filter(EffectStyle.id == style_id).first()
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"EffectStyle with id {style_id} not found"
        )
    
    return EffectStyleResponse(
        id=style.id,
        name=style.name,
        style_type=style.style_type,
        subtype=style.subtype,
        description=style.description,
        process_verb=style.process_verb,
        execution_probability=style.execution_probability,
        effector_config=style.effector_config,
        style_attributes=style.style_attributes,
        created_by_id=style.created_by_id,
        created_at=style.created_at.isoformat() if style.created_at else "",
        updated_at=style.updated_at.isoformat() if style.updated_at else None,
    )


@router.post("/", response_model=EffectStyleResponse)
async def create_effect_style(
    style_config: EffectStyleConfig,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
    db: Session = Depends(get_db)
):
    """
    Create a new effect style and save to library.
    
    Args:
        style_config: EffectStyle configuration
        current_user: Current authenticated user
        
    Returns:
        Created EffectStyle
    """
    # Validate style_type
    valid_types = ["Physical", "Spell", "Buff", "Debuff", "Regen", "Process"]
    if style_config.style_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid style_type: {style_config.style_type}. Must be one of {valid_types}"
        )
    
    # Validate execution_probability
    if not 0.0 <= style_config.execution_probability <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="execution_probability must be between 0.0 and 1.0"
        )
    
    # Determine effector_config - support both single effector and multiple effectors
    if style_config.effectors is not None:
        effector_config = style_config.effectors
    elif style_config.effector is not None:
        effector_config = style_config.effector
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'effector' or 'effectors' must be provided"
        )
    
    # Create database record
    db_style = EffectStyle(
        name=style_config.name,
        style_type=style_config.style_type,
        subtype=style_config.subtype,
        description=style_config.description or "",
        process_verb=style_config.process_verb or style_config.subtype,
        execution_probability=style_config.execution_probability,
        effector_config=effector_config,
        style_attributes=style_config.style_attributes,
        created_by_id=current_user.id,
    )
    
    db.add(db_style)
    db.commit()
    db.refresh(db_style)
    
    return EffectStyleResponse(
        id=db_style.id,
        name=db_style.name,
        style_type=db_style.style_type,
        subtype=db_style.subtype,
        description=db_style.description,
        process_verb=db_style.process_verb,
        execution_probability=db_style.execution_probability,
        effector_config=db_style.effector_config,
        style_attributes=db_style.style_attributes,
        created_by_id=db_style.created_by_id,
        created_at=db_style.created_at.isoformat() if db_style.created_at else "",
        updated_at=db_style.updated_at.isoformat() if db_style.updated_at else None,
    )


@router.put("/{style_id}", response_model=EffectStyleResponse)
async def update_effect_style(
    style_id: int,
    style_config: EffectStyleConfig,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
    db: Session = Depends(get_db)
):
    """Update an existing effect style."""
    db_style = db.query(EffectStyle).filter(EffectStyle.id == style_id).first()
    
    if not db_style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"EffectStyle with id {style_id} not found"
        )
    
    # Determine effector_config - support both single effector and multiple effectors
    if style_config.effectors is not None:
        effector_config = style_config.effectors
    elif style_config.effector is not None:
        effector_config = style_config.effector
    else:
        # Keep existing if neither provided
        effector_config = db_style.effector_config
    
    # Update fields
    db_style.name = style_config.name
    db_style.style_type = style_config.style_type
    db_style.subtype = style_config.subtype
    db_style.description = style_config.description or ""
    db_style.process_verb = style_config.process_verb or style_config.subtype
    db_style.execution_probability = style_config.execution_probability
    db_style.effector_config = effector_config
    if style_config.style_attributes is not None:
        db_style.style_attributes = style_config.style_attributes
    
    db.commit()
    db.refresh(db_style)
    
    return EffectStyleResponse(
        id=db_style.id,
        name=db_style.name,
        style_type=db_style.style_type,
        subtype=db_style.subtype,
        description=db_style.description,
        process_verb=db_style.process_verb,
        execution_probability=db_style.execution_probability,
        effector_config=db_style.effector_config,
        style_attributes=db_style.style_attributes,
        created_by_id=db_style.created_by_id,
        created_at=db_style.created_at.isoformat() if db_style.created_at else "",
        updated_at=db_style.updated_at.isoformat() if db_style.updated_at else None,
    )


@router.delete("/{style_id}")
async def delete_effect_style(
    style_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
    db: Session = Depends(get_db)
):
    """Delete an effect style."""
    db_style = db.query(EffectStyle).filter(EffectStyle.id == style_id).first()
    
    if not db_style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"EffectStyle with id {style_id} not found"
        )
    
    db.delete(db_style)
    db.commit()
    
    return {"message": f"EffectStyle {style_id} deleted successfully"}

