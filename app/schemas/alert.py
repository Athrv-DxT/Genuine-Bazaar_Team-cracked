"""
Alert schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.alert import AlertType, AlertPriority, AlertStatus


class AlertCreate(BaseModel):
    """Alert creation schema (internal)"""
    user_id: int
    alert_type: str
    priority: str = "medium"
    title: str
    message: str
    keyword: Optional[str] = None
    category: Optional[str] = None
    context_data: Dict[str, Any] = {}
    predicted_impact: Optional[float] = None
    confidence_score: float = 0.0


class AlertResponse(BaseModel):
    """Alert response schema"""
    id: int
    alert_type: str
    priority: str
    status: str
    title: str
    message: str
    keyword: Optional[str]
    category: Optional[str]
    context_data: Dict[str, Any]
    predicted_impact: Optional[float]
    confidence_score: float
    created_at: datetime
    read_at: Optional[datetime]
    acted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """Alert update schema"""
    status: Optional[str] = None  # read, acted, dismissed


