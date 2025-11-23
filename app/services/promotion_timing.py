"""
Promotion Timing Engine
Identifies optimal windows for promotions based on sentiment, festivals, footfall, competitor activity
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertType, AlertPriority
from app.models.user import User
from app.services.trends_service import TrendsService
from app.services.holiday_service import HolidayService

logger = logging.getLogger(__name__)


class PromotionTimingEngine:
    """Identifies optimal promotion timing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.trends_service = TrendsService()
        self.holiday_service = HolidayService()
    
    def find_promotion_windows(
        self,
        user: User,
        keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """Find optimal promotion timing windows"""
        alerts = []
        
        # Get user's tracked keywords
        if not keywords:
            tracked = user.tracked_keywords
            keywords = [tk.keyword for tk in tracked if tk.is_active]
        
        if not keywords:
            return alerts
        
        for keyword in keywords:
            # Check sentiment peaks
            sentiment_alerts = self._check_sentiment_peaks(user, keyword)
            alerts.extend(sentiment_alerts)
            
            # Check festival priming days
            festival_alerts = self._check_festival_priming(user, keyword)
            alerts.extend(festival_alerts)
            
            # Check footfall hours
            footfall_alerts = self._check_footfall_hours(user, keyword)
            alerts.extend(footfall_alerts)
            
            # Check competitor inactivity
            competitor_alerts = self._check_competitor_inactivity(user, keyword)
            alerts.extend(competitor_alerts)
        
        return alerts
    
    def _check_sentiment_peaks(
        self,
        user: User,
        keyword: str
    ) -> List[Dict]:
        """Check for sentiment peaks (high trust/positive sentiment)"""
        alerts = []
        
        try:
            # Get trend score as proxy for sentiment
            trend_score = self.trends_service.get_trend_score(keyword)
            
            if trend_score and trend_score > 65:
                # High sentiment/interest
                alerts.append({
                    "user_id": user.id,
                    "alert_type": AlertType.SENTIMENT_PEAK.value,
                    "priority": AlertPriority.HIGH.value,
                    "title": f"Sentiment Peak: Run {keyword} Promotion Now",
                    "message": f"Trust and interest for {keyword} is rising (score: {trend_score}/100). "
                             f"Run promotion now for 3x conversion rate.",
                    "keyword": keyword,
                    "context_data": {
                        "sentiment_score": trend_score,
                        "recommended_duration": "3-5 days",
                        "expected_roi_multiplier": 3.0
                    },
                    "predicted_impact": trend_score * 0.6,
                    "confidence_score": trend_score / 100
                })
        
        except Exception as e:
            logger.error(f"Error checking sentiment peaks: {e}")
        
        return alerts
    
    def _check_festival_priming(
        self,
        user: User,
        keyword: str
    ) -> List[Dict]:
        """Check for festival priming days (days before festival when promotions work best)"""
        alerts = []
        
        try:
            # Get upcoming holidays
            holidays = self.holiday_service.get_upcoming_holidays(
                country=user.location_country,
                days_ahead=14
            )
            
            for holiday in holidays:
                holiday_name = holiday.get("name", "")
                date_str = holiday.get("date", "")
                
                try:
                    holiday_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    days_until = (holiday_date - datetime.now()).days
                    
                    # Prime window: 3-7 days before festival
                    if 3 <= days_until <= 7:
                        festival_keywords_map = {
                            "diwali": ["lights", "candles", "sweets", "gifts", "clothes", "electronics"],
                            "holi": ["colors", "water guns", "clothes", "sweets"],
                            "eid": ["clothes", "food", "gifts"],
                            "christmas": ["gifts", "decorations", "clothes", "toys"],
                            "new year": ["party", "clothes", "gifts", "decorations"]
                        }
                        
                        for festival, keywords in festival_keywords_map.items():
                            if festival.lower() in holiday_name.lower():
                                if any(kw in keyword.lower() for kw in keywords):
                                    alerts.append({
                                        "user_id": user.id,
                                        "alert_type": AlertType.PROMOTION_TIMING.value,
                                        "priority": AlertPriority.HIGH.value,
                                        "title": f"Festival Priming Window: {holiday_name}",
                                        "message": f"{holiday_name} is in {days_until} days. "
                                                 f"This is the PRIME window for {keyword} promotions. "
                                                 f"Launch now for maximum ROI!",
                                        "keyword": keyword,
                                        "context_data": {
                                            "holiday_name": holiday_name,
                                            "holiday_date": date_str,
                                            "days_until": days_until,
                                            "window_type": "priming"
                                        },
                                        "predicted_impact": 70,
                                        "confidence_score": 0.85
                                    })
                
                except Exception as e:
                    logger.error(f"Error parsing holiday date: {e}")
        
        except Exception as e:
            logger.error(f"Error checking festival priming: {e}")
        
        return alerts
    
    def _check_footfall_hours(
        self,
        user: User,
        keyword: str
    ) -> List[Dict]:
        """Check for high footfall hours (peak shopping times)"""
        alerts = []
        
        try:
            # Get current hour
            current_hour = datetime.now().hour
            
            # High footfall windows (typically)
            # Morning: 10-12, Evening: 6-9, Weekend: 10-8
            is_weekend = datetime.now().weekday() >= 5
            
            high_footfall_windows = []
            if is_weekend:
                high_footfall_windows = [(10, 20)]  # 10 AM to 8 PM on weekends
            else:
                high_footfall_windows = [(10, 12), (18, 21)]  # Morning and evening on weekdays
            
            in_window = False
            for start, end in high_footfall_windows:
                if start <= current_hour < end:
                    in_window = True
                    break
            
            if in_window:
                alerts.append({
                    "user_id": user.id,
                    "alert_type": AlertType.FOOTFALL_WINDOW.value,
                    "priority": AlertPriority.MEDIUM.value,
                    "title": f"High Footfall Window: Promote {keyword} Now",
                    "message": f"Currently in high footfall window ({current_hour}:00). "
                             f"Boost {keyword} visibility for immediate impact.",
                    "keyword": keyword,
                    "context_data": {
                        "current_hour": current_hour,
                        "is_weekend": is_weekend,
                        "window_type": "footfall"
                    },
                    "predicted_impact": 25,
                    "confidence_score": 0.6
                })
        
        except Exception as e:
            logger.error(f"Error checking footfall hours: {e}")
        
        return alerts
    
    def _check_competitor_inactivity(
        self,
        user: User,
        keyword: str
    ) -> List[Dict]:
        """Check for competitor inactivity windows (when competitors aren't promoting)"""
        alerts = []
        
        try:
            # In a real implementation, monitor competitor promotion activity
            # For now, simulate detection
            
            # Typically, competitors are less active:
            # - Late night/early morning
            # - Mid-week lulls
            # - Post-festival periods
            
            current_hour = datetime.now().hour
            current_weekday = datetime.now().weekday()
            
            # Late night/early morning window (11 PM - 6 AM)
            if current_hour >= 23 or current_hour < 6:
                alerts.append({
                    "user_id": user.id,
                    "alert_type": AlertType.PROMOTION_TIMING.value,
                    "priority": AlertPriority.MEDIUM.value,
                    "title": f"Competitor Inactivity Window: {keyword}",
                    "message": f"Low competitor activity detected. "
                             f"Run {keyword} promotion now for better visibility.",
                    "keyword": keyword,
                    "context_data": {
                        "window_type": "competitor_inactivity",
                        "current_hour": current_hour,
                        "advantage": "less_competition"
                    },
                    "predicted_impact": 20,
                    "confidence_score": 0.5
                })
        
        except Exception as e:
            logger.error(f"Error checking competitor inactivity: {e}")
        
        return alerts


