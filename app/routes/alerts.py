"""
Alert routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.auth import get_current_active_user
from app.models.user import User
from app.models.alert import Alert, AlertStatus
from app.schemas.alert import AlertResponse, AlertUpdate
from app.services.demand_detector import DemandDetector
from app.services.promotion_timing import PromotionTimingEngine

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alerts for current user"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/new", response_model=List[AlertResponse])
async def get_new_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get unread alerts"""
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.status == AlertStatus.NEW.value
    ).order_by(Alert.created_at.desc()).all()
    return alerts


@router.post("/generate")
async def generate_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually trigger alert generation"""
    # Detect demand peaks
    demand_detector = DemandDetector(db)
    demand_alerts = demand_detector.detect_demand_peaks(current_user)
    
    # Find promotion windows
    promotion_engine = PromotionTimingEngine(db)
    promotion_alerts = promotion_engine.find_promotion_windows(current_user)
    
    # Combine and save alerts
    all_alerts = demand_alerts + promotion_alerts
    created_count = 0
    
    for alert_data in all_alerts:
        # Check if similar alert already exists (avoid duplicates)
        existing = db.query(Alert).filter(
            Alert.user_id == alert_data["user_id"],
            Alert.alert_type == alert_data["alert_type"],
            Alert.keyword == alert_data.get("keyword"),
            Alert.status == AlertStatus.NEW.value
        ).first()
        
        if not existing:
            alert = Alert(**alert_data)
            db.add(alert)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"Generated {created_count} new alerts",
        "total_detected": len(all_alerts),
        "created": created_count
    }


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update alert status"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert_update.status:
        alert.status = alert_update.status
        if alert_update.status == AlertStatus.READ.value:
            alert.read_at = datetime.utcnow()
        elif alert_update.status == AlertStatus.ACTED.value:
            alert.acted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted"}


