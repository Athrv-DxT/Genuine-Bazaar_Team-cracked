"""
Tracked keywords routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.auth import get_current_active_user
from app.models.user import User, TrackedKeyword

router = APIRouter(prefix="/keywords", tags=["keywords"])


class KeywordCreate(BaseModel):
    keyword: str
    category: str = None


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    category: str = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[KeywordResponse])
async def get_keywords(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's tracked keywords"""
    keywords = db.query(TrackedKeyword).filter(
        TrackedKeyword.user_id == current_user.id
    ).all()
    return keywords


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def add_keyword(
    keyword_data: KeywordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a tracked keyword"""
    # Check if already exists
    existing = db.query(TrackedKeyword).filter(
        TrackedKeyword.user_id == current_user.id,
        TrackedKeyword.keyword == keyword_data.keyword
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword already tracked"
        )
    
    keyword = TrackedKeyword(
        user_id=current_user.id,
        keyword=keyword_data.keyword,
        category=keyword_data.category,
        is_active=True
    )
    
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    
    return keyword


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a tracked keyword"""
    keyword = db.query(TrackedKeyword).filter(
        TrackedKeyword.id == keyword_id,
        TrackedKeyword.user_id == current_user.id
    ).first()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    db.delete(keyword)
    db.commit()
    
    return {"message": "Keyword deleted"}

