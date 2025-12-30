"""Effector API routes for managing effectors."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.database import get_db
from src.database.models import User
from src.core.security import get_current_active_user, require_role, UserRole

router = APIRouter()


class EffectorConfig(BaseModel):
    """Effector configuration model."""
    effector_type: str
    effector_name: str
    # Additional fields vary by effector type
    damage_subtype: Optional[str] = None
    element_type: Optional[str] = None
    attribute_type: Optional[str] = None
    affected_attributes: Optional[List[str]] = None
    base_damage: Optional[float] = None
    base_restoration: Optional[float] = None
    base_buff: Optional[float] = None
    base_debuff: Optional[float] = None
    duration: Optional[float] = None
    stackable: Optional[bool] = None
    distribution_parameters: Optional[dict] = None
    process_config: Optional[dict] = None
    input_effectors: Optional[List[str]] = None
    output_effectors: Optional[List[str]] = None


class EffectorResponse(BaseModel):
    """Effector response model."""
    effector_type: str
    effector_name: str
    config: dict

    class Config:
        from_attributes = True


@router.get("/types", response_model=List[str])
async def get_effector_types():
    """Get list of available effector types."""
    return ["damage", "regenerative", "buff", "debuff", "process"]


@router.get("/", response_model=List[EffectorResponse])
async def list_effectors(
    effector_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List available effectors.
    
    For now, returns template effectors. In the future, this could
    return saved effector configurations from the database.
    """
    # Return template effectors based on type
    templates = []
    
    if effector_type is None or effector_type == "damage":
        templates.append({
            "effector_type": "damage",
            "effector_name": "physical_damage",
            "config": {
                "damage_subtype": "physical",
                "base_damage": 10.0,
                "distribution_parameters": {
                    "type": "gaussian",
                    "params": {"mean": 10.0, "std_dev": 2.0}
                }
            }
        })
        templates.append({
            "effector_type": "damage",
            "effector_name": "elemental_damage",
            "config": {
                "damage_subtype": "elemental",
                "element_type": "fire",
                "base_damage": 10.0,
                "distribution_parameters": {
                    "type": "gaussian",
                    "params": {"mean": 10.0, "std_dev": 2.0}
                }
            }
        })
    
    if effector_type is None or effector_type == "regenerative":
        templates.append({
            "effector_type": "regenerative",
            "effector_name": "health_restoration",
            "config": {
                "attribute_type": "health",
                "base_restoration": 10.0,
                "distribution_parameters": {
                    "type": "gaussian",
                    "params": {"mean": 10.0, "std_dev": 2.0}
                }
            }
        })
    
    if effector_type is None or effector_type == "buff":
        templates.append({
            "effector_type": "buff",
            "effector_name": "strength_buff",
            "config": {
                "affected_attributes": ["str"],
                "base_buff": 5.0,
                "duration": 60.0,
                "stackable": False,
                "distribution_parameters": {
                    "type": "gaussian",
                    "params": {"mean": 5.0, "std_dev": 1.0}
                }
            }
        })
    
    if effector_type is None or effector_type == "debuff":
        templates.append({
            "effector_type": "debuff",
            "effector_name": "weakness_debuff",
            "config": {
                "affected_attributes": ["str"],
                "base_debuff": 5.0,
                "duration": 60.0,
                "stackable": False,
                "distribution_parameters": {
                    "type": "gaussian",
                    "params": {"mean": 5.0, "std_dev": 1.0}
                }
            }
        })
    
    if effector_type is None or effector_type == "process":
        templates.append({
            "effector_type": "process",
            "effector_name": "custom_process",
            "config": {
                "process_config": {},
                "input_effectors": [],
                "output_effectors": []
            }
        })
    
    return templates


@router.post("/validate", response_model=dict)
async def validate_effector_config(
    config: EffectorConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate an effector configuration.
    
    Returns validation result and any errors.
    """
    errors = []
    
    # Validate effector type
    valid_types = ["damage", "regenerative", "buff", "debuff", "process"]
    if config.effector_type not in valid_types:
        errors.append(f"Invalid effector_type: {config.effector_type}")
    
    # Type-specific validation
    if config.effector_type == "damage":
        if not config.damage_subtype:
            errors.append("damage_subtype is required for damage effectors")
        if config.damage_subtype == "elemental" and not config.element_type:
            errors.append("element_type is required for elemental damage")
        if config.base_damage is None:
            errors.append("base_damage is required for damage effectors")
    
    elif config.effector_type == "regenerative":
        if not config.attribute_type:
            errors.append("attribute_type is required for regenerative effectors")
        if config.base_restoration is None:
            errors.append("base_restoration is required for regenerative effectors")
    
    elif config.effector_type in ["buff", "debuff"]:
        if not config.affected_attributes:
            errors.append("affected_attributes is required for buff/debuff effectors")
        if config.effector_type == "buff" and config.base_buff is None:
            errors.append("base_buff is required for buff effectors")
        if config.effector_type == "debuff" and config.base_debuff is None:
            errors.append("base_debuff is required for debuff effectors")
    
    elif config.effector_type == "process":
        if config.process_config is None:
            errors.append("process_config is required for process effectors")
    
    # Validate distribution parameters if present
    if config.distribution_parameters:
        dist_type = config.distribution_parameters.get("type")
        if dist_type not in ["uniform", "gaussian", "skewnorm", "bimodal", "die_roll"]:
            errors.append(f"Invalid distribution type: {dist_type}")
    
    if errors:
        return {
            "valid": False,
            "errors": errors
        }
    
    return {
        "valid": True,
        "message": "Effector configuration is valid"
    }


@router.post("/create", response_model=EffectorResponse)
async def create_effector(
    config: EffectorConfig,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.DESIGNER)),
    db: Session = Depends(get_db)
):
    """
    Create a new effector configuration.
    
    For now, this validates and returns the config. In the future,
    this could save effector templates to the database.
    """
    # Validate first
    validation = await validate_effector_config(config, current_user, db)
    if not validation.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation.get("errors", ["Invalid configuration"])
        )
    
    # Convert to response format
    response_config = config.dict(exclude_none=True)
    
    return {
        "effector_type": config.effector_type,
        "effector_name": config.effector_name,
        "config": response_config
    }

