"""
Background job to generate alerts for all active users
"""
import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.alert import Alert, AlertStatus
from app.services.demand_detector import DemandDetector
from app.services.promotion_timing import PromotionTimingEngine

logger = logging.getLogger(__name__)


def generate_alerts_for_all_users():
    """Generate alerts for all active users"""
    db: Session = SessionLocal()
    try:
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        total_alerts = 0
        for user in users:
            try:
                # Detect demand peaks
                demand_detector = DemandDetector(db)
                demand_alerts = demand_detector.detect_demand_peaks(user)
                
                # Find promotion windows
                promotion_engine = PromotionTimingEngine(db)
                promotion_alerts = promotion_engine.find_promotion_windows(user)
                
                # Combine alerts
                all_alerts = demand_alerts + promotion_alerts
                
                # Save new alerts (avoid duplicates)
                for alert_data in all_alerts:
                    existing = db.query(Alert).filter(
                        Alert.user_id == alert_data["user_id"],
                        Alert.alert_type == alert_data["alert_type"],
                        Alert.keyword == alert_data.get("keyword"),
                        Alert.status == AlertStatus.NEW.value
                    ).first()
                    
                    if not existing:
                        alert = Alert(**alert_data)
                        db.add(alert)
                        total_alerts += 1
                
                db.commit()
                logger.info(f"Generated alerts for user {user.id}: {len(all_alerts)} detected, {total_alerts} new")
                
            except Exception as e:
                logger.error(f"Error generating alerts for user {user.id}: {e}")
                db.rollback()
        
        logger.info(f"Alert generation complete: {total_alerts} new alerts created")
        return total_alerts
        
    except Exception as e:
        logger.error(f"Error in alert generation job: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    # Run manually for testing
    generate_alerts_for_all_users()


