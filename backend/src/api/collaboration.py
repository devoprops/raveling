"""Collaboration API routes for notes and user colors."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.database import get_db
from src.database.models import User, CollaborationNote
from src.core.security import get_current_active_user

router = APIRouter()


class NoteContent(BaseModel):
    """Note content model."""
    content: str


class NoteResponse(BaseModel):
    """Note response model."""
    id: int
    designer_type: str
    content: str
    created_by_id: int
    updated_by_id: int
    created_at: str
    updated_at: Optional[str]
    created_by_username: Optional[str] = None
    updated_by_username: Optional[str] = None

    class Config:
        from_attributes = True


class UserColorResponse(BaseModel):
    """User color response model."""
    user_color: Optional[str]


class UserColorUpdate(BaseModel):
    """User color update model."""
    user_color: str


@router.get("/notes/{designer_type}", response_model=NoteResponse)
async def get_note(
    designer_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notes for a specific designer type."""
    note = db.query(CollaborationNote).filter(
        CollaborationNote.designer_type == designer_type
    ).first()
    
    if not note:
        # Return empty note structure
        return NoteResponse(
            id=0,
            designer_type=designer_type,
            content="",
            created_by_id=current_user.id,
            updated_by_id=current_user.id,
            created_at="",
            updated_at=None,
        )
    
    return NoteResponse(
        id=note.id,
        designer_type=note.designer_type,
        content=note.content,
        created_by_id=note.created_by_id,
        updated_by_id=note.updated_by_id,
        created_at=note.created_at.isoformat() if note.created_at else "",
        updated_at=note.updated_at.isoformat() if note.updated_at else None,
        created_by_username=note.created_by.username if note.created_by else None,
        updated_by_username=note.updated_by.username if note.updated_by else None,
    )


@router.post("/notes/{designer_type}", response_model=NoteResponse)
async def upsert_note(
    designer_type: str,
    note_content: NoteContent,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create or update notes for a designer type (upsert)."""
    # Validate designer_type
    valid_types = [
        "weapons", "skills", "spells", "wearables", 
        "consumables", "characters", "zones", "general", "quick_notes"
    ]
    if designer_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid designer_type: {designer_type}. Must be one of {valid_types}"
        )
    
    # Check if note exists
    note = db.query(CollaborationNote).filter(
        CollaborationNote.designer_type == designer_type
    ).first()
    
    if note:
        # Update existing note
        note.content = note_content.content
        note.updated_by_id = current_user.id
        db.commit()
        db.refresh(note)
    else:
        # Create new note
        note = CollaborationNote(
            designer_type=designer_type,
            content=note_content.content,
            created_by_id=current_user.id,
            updated_by_id=current_user.id,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
    
    return NoteResponse(
        id=note.id,
        designer_type=note.designer_type,
        content=note.content,
        created_by_id=note.created_by_id,
        updated_by_id=note.updated_by_id,
        created_at=note.created_at.isoformat() if note.created_at else "",
        updated_at=note.updated_at.isoformat() if note.updated_at else None,
        created_by_username=note.created_by.username if note.created_by else None,
        updated_by_username=note.updated_by.username if note.updated_by else None,
    )


@router.get("/user-color", response_model=UserColorResponse)
async def get_user_color(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's color."""
    return UserColorResponse(user_color=current_user.user_color)


@router.put("/user-color", response_model=UserColorResponse)
async def update_user_color(
    color_update: UserColorUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's color."""
    # Validate hex color format
    color = color_update.user_color.strip()
    if not color.startswith("#") or len(color) != 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid color format. Must be a hex color (e.g., #4a90e2)"
        )
    
    try:
        int(color[1:], 16)  # Validate hex
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hex color value"
        )
    
    current_user.user_color = color
    db.commit()
    db.refresh(current_user)
    
    return UserColorResponse(user_color=current_user.user_color)

