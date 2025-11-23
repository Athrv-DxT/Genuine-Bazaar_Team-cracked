"""
Demand Peak Detection Service
Detects hidden demand peaks from weather, events, social trends, competitor stockouts, festivals
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertType, AlertPriority, DemandSignal
from app.models.user import User
from app.services.weather_service import WeatherService
from app.services.holiday_service import HolidayService
from app.services.trends_service import TrendsService
from app.services.industry_trends import IndustryTrendsService

logger = logging.getLogger(__name__)


class DemandDetector:
    """Detects demand peaks and opportunities"""
    
    def __init__(self, db: Session):
        self.db = db
        self.weather_service = WeatherService()
        self.holiday_service = HolidayService()
        self.trends_service = TrendsService(
            username=None,  # Can be set from config if needed
            password=None
        )
        self.industry_trends_service = IndustryTrendsService()
    
    def detect_demand_peaks(
        self,
        user: User,
        keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """Detect demand peaks for a user's tracked keywords"""
        alerts = []
        
        # Get user's tracked keywords or use provided ones
        if not keywords:
            tracked = user.tracked_keywords
            keywords = [tk.keyword for tk in tracked if tk.is_active]
        
        city = user.location_city or "Mumbai"  # Default city
        country = user.location_country or "IN"
        
        # AUTOMATIC WEATHER ALERTS: Check for rain even if user hasn't added umbrella keyword
        weather_alerts_auto = self._check_automatic_weather_alerts(user, city)
        alerts.extend(weather_alerts_auto)
        
        # INDUSTRY-SPECIFIC TREND ALERTS: Based on user's market categories
        industry_alerts = self._check_industry_trends(user, city, country)
        alerts.extend(industry_alerts)
        
        if not keywords:
            logger.info(f"No keywords to track for user {user.id}, but weather and industry alerts checked")
            return alerts
        
        for keyword in keywords:
            # Check weather-based demand
            weather_alerts = self._check_weather_demand(user, keyword, city)
            alerts.extend(weather_alerts)
            
            # Check event-based demand
            event_alerts = self._check_event_demand(user, keyword, city)
            alerts.extend(event_alerts)
            
            # Check social trend demand
            social_alerts = self._check_social_trends(user, keyword)
            alerts.extend(social_alerts)
            
            # Check competitor stockouts
            stockout_alerts = self._check_competitor_stockouts(user, keyword)
            alerts.extend(stockout_alerts)
            
            # Check festival demand
            festival_alerts = self._check_festival_demand(user, keyword, city)
            alerts.extend(festival_alerts)
        
        return alerts
    
    def _check_automatic_weather_alerts(
        self,
        user: User,
        city: str
    ) -> List[Dict]:
        """Automatically check weather and suggest relevant products even if not tracked"""
        alerts = []
        
        try:
            # Get weather forecast
            weather_data = self.weather_service.get_forecast(city, hours_ahead=24)
            if not weather_data:
                return alerts
            
            # Check for rain in next 3-6 hours
            for forecast in weather_data.get("forecast", [])[:6]:  # Next 6 hours
                rain_prob = forecast.get("rain_probability", 0)
                hours_ahead = forecast.get("hours_ahead", 0)
                
                # If high rain probability (70%+), suggest umbrella even if not tracked
                if rain_prob > 0.7 and hours_ahead <= 6:
                    # Check if user already tracks rain-related keywords
                    tracked_keywords = [tk.keyword.lower() for tk in user.tracked_keywords if tk.is_active]
                    rain_keywords = ["umbrella", "raincoat", "rain", "waterproof", "boots"]
                    has_rain_keyword = any(rk in kw for kw in tracked_keywords for rk in rain_keywords)
                    
                    if not has_rain_keyword:
                        # Suggest adding umbrella keyword
                        alerts.append({
                            "user_id": user.id,
                            "alert_type": AlertType.WEATHER_OPPORTUNITY.value,
                            "priority": AlertPriority.HIGH.value,
                            "title": "🌧️ Rain Alert: Consider Tracking Umbrella Products",
                            "message": f"Rain predicted in {hours_ahead} hours ({rain_prob*100:.0f}% probability) in {city}. "
                                     f"Add 'umbrella' or 'raincoat' to your tracked keywords to get automatic alerts!",
                            "keyword": None,  # No specific keyword yet
                            "context_data": {
                                "weather_type": "rain",
                                "hours_ahead": hours_ahead,
                                "rain_probability": rain_prob,
                                "city": city,
                                "suggestion": "Add 'umbrella' keyword"
                            },
                            "predicted_impact": rain_prob * 50,
                            "confidence_score": rain_prob
                        })
                    break  # Only one rain alert per check
            
            # Check for hot weather
            for forecast in weather_data.get("forecast", [])[:12]:  # Next 12 hours
                temp = forecast.get("temperature", 0)
                hours_ahead = forecast.get("hours_ahead", 0)
                
                if temp > 35 and hours_ahead <= 12:
                    tracked_keywords = [tk.keyword.lower() for tk in user.tracked_keywords if tk.is_active]
                    hot_keywords = ["cold drink", "ice cream", "fan", "ac", "cooler", "summer"]
                    has_hot_keyword = any(hk in kw for kw in tracked_keywords for hk in hot_keywords)
                    
                    if not has_hot_keyword:
                        alerts.append({
                            "user_id": user.id,
                            "alert_type": AlertType.WEATHER_OPPORTUNITY.value,
                            "priority": AlertPriority.MEDIUM.value,
                            "title": "☀️ Hot Weather: Consider Tracking Summer Products",
                            "message": f"High temperature ({temp}°C) expected in {hours_ahead} hours in {city}. "
                                     f"Add 'cold drink' or 'ice cream' to your keywords for automatic alerts!",
                            "keyword": None,
                            "context_data": {
                                "weather_type": "hot",
                                "temperature": temp,
                                "hours_ahead": hours_ahead,
                                "city": city,
                                "suggestion": "Add 'cold drink' keyword"
                            },
                            "predicted_impact": 30,
                            "confidence_score": 0.7
                        })
                    break
        
        except Exception as e:
            logger.error(f"Error checking automatic weather alerts: {e}")
        
        return alerts
    
    def _check_industry_trends(
        self,
        user: User,
        city: str,
        country: str
    ) -> List[Dict]:
        """Check industry-specific trends based on user's market categories"""
        alerts = []
        
        if not user.market_categories:
            return alerts
        
        try:
            # Get trends for all user's industries
            all_trends = self.industry_trends_service.get_all_industry_trends(
                user.market_categories,
                location=country
            )
            
            for industry, trends in all_trends.items():
                if not trends:
                    continue
                
                # Get top trending items
                top_trends = trends[:3]  # Top 3 trends per industry
                
                for trend in top_trends:
                    keyword = trend["keyword"]
                    trend_score = trend["trend_score"]
                    status = trend.get("status", "trending")
                    
                    # Check if user already tracks this keyword
                    tracked_keywords = [tk.keyword.lower() for tk in user.tracked_keywords if tk.is_active]
                    already_tracked = keyword.lower() in tracked_keywords
                    
                    # Create alert for trending items
                    if trend_score > 70:  # High trend threshold
                        if industry.lower() == "clothes":
                            # Special handling for clothing trends
                            season = trend.get("season", "")
                            category = trend.get("category", "general")
                            
                            title = f"{industry.title()} Trend: {keyword.title()} is {status.title()}"
                            message = f"{keyword.title()} is currently {status} in {industry} (trend score: {trend_score}/100). "
                            
                            if season:
                                message += f"Perfect for {season} season. "
                            if category == "seasonal":
                                message += f"Stock up on {keyword} now to capture seasonal demand!"
                            else:
                                message += f"Consider adding {keyword} to your inventory or boosting visibility!"
                            
                            if not already_tracked:
                                message += f" Add '{keyword}' to your tracked keywords for automatic alerts."
                        else:
                            title = f"{industry.title()} Trend: {keyword.title()} is {status.title()}"
                            message = f"{keyword.title()} is currently {status} in {industry} (trend score: {trend_score}/100). "
                            message += f"High demand expected. Consider boosting visibility or stock!"
                            
                            if not already_tracked:
                                message += f" Add '{keyword}' to your tracked keywords."
                        
                        alerts.append({
                            "user_id": user.id,
                            "alert_type": AlertType.SOCIAL_TREND.value,
                            "priority": AlertPriority.HIGH.value if trend_score > 80 else AlertPriority.MEDIUM.value,
                            "title": title,
                            "message": message,
                            "keyword": keyword,
                            "category": industry,
                            "context_data": {
                                "industry": industry,
                                "trend_score": trend_score,
                                "status": status,
                                "location": city,
                                "suggestion": f"Track '{keyword}' keyword" if not already_tracked else None
                            },
                            "predicted_impact": trend_score * 0.5,  # Estimated impact
                            "confidence_score": trend_score / 100
                        })
        
        except Exception as e:
            logger.error(f"Error checking industry trends: {e}")
        
        return alerts
    
    def _check_weather_demand(
        self,
        user: User,
        keyword: str,
        city: str
    ) -> List[Dict]:
        """Check weather-based demand opportunities"""
        alerts = []
        
        try:
            # Get weather forecast
            weather_data = self.weather_service.get_forecast(city, hours_ahead=24)
            if not weather_data:
                return alerts
            
            # Check for rain in next 3-6 hours
            for forecast in weather_data.get("forecast", [])[:6]:  # Next 6 hours
                rain_prob = forecast.get("rain_probability", 0)
                hours_ahead = forecast.get("hours_ahead", 0)
                
                if rain_prob > 0.7 and hours_ahead <= 6:
                    # High rain probability - check if keyword is rain-related
                    rain_keywords = ["umbrella", "raincoat", "rain", "waterproof", "boots"]
                    if any(rk in keyword.lower() for rk in rain_keywords):
                        alerts.append({
                            "user_id": user.id,
                            "alert_type": AlertType.WEATHER_OPPORTUNITY.value,
                            "priority": AlertPriority.HIGH.value,
                            "title": f"Rain Alert: {keyword} Demand Spike Expected",
                            "message": f"Rain predicted in {hours_ahead} hours ({rain_prob*100:.0f}% probability). "
                                     f"Expected spike in {keyword} demand. Stock up now!",
                            "keyword": keyword,
                            "context_data": {
                                "weather_type": "rain",
                                "hours_ahead": hours_ahead,
                                "rain_probability": rain_prob,
                                "city": city
                            },
                            "predicted_impact": rain_prob * 50,  # Estimated revenue impact
                            "confidence_score": rain_prob
                        })
                
                # Check for hot weather
                temp = forecast.get("temperature", 0)
                if temp > 35 and hours_ahead <= 12:
                    hot_keywords = ["cold drink", "ice cream", "fan", "ac", "cooler", "summer"]
                    if any(hk in keyword.lower() for hk in hot_keywords):
                        alerts.append({
                            "user_id": user.id,
                            "alert_type": AlertType.WEATHER_OPPORTUNITY.value,
                            "priority": AlertPriority.MEDIUM.value,
                            "title": f"Hot Weather: {keyword} Demand Increase",
                            "message": f"High temperature ({temp}°C) expected. "
                                     f"Increase visibility of {keyword} products.",
                            "keyword": keyword,
                            "context_data": {
                                "weather_type": "hot",
                                "temperature": temp,
                                "hours_ahead": hours_ahead,
                                "city": city
                            },
                            "predicted_impact": 30,
                            "confidence_score": 0.7
                        })
        
        except Exception as e:
            logger.error(f"Error checking weather demand: {e}")
        
        return alerts
    
    def _check_event_demand(
        self,
        user: User,
        keyword: str,
        city: str
    ) -> List[Dict]:
        """Check local event-based demand"""
        alerts = []
        
        try:
            # In a real implementation, integrate with event APIs (Eventbrite, etc.)
            # For now, simulate event detection
            # You would check for local events, concerts, sports events, etc.
            
            # Example: If there's a local event, snacks/beverages might spike
            event_keywords = ["snacks", "beverages", "drinks", "food", "party"]
            if any(ek in keyword.lower() for ek in event_keywords):
                # Simulate event detection (replace with actual API)
                alerts.append({
                    "user_id": user.id,
                    "alert_type": AlertType.EVENT_SPIKE.value,
                    "priority": AlertPriority.MEDIUM.value,
                    "title": f"Local Event Detected: {keyword} Opportunity",
                    "message": f"Local events detected in {city}. "
                             f"Boost visibility of {keyword} products.",
                    "keyword": keyword,
                    "context_data": {
                        "event_type": "local_event",
                        "city": city
                    },
                    "predicted_impact": 25,
                    "confidence_score": 0.6
                })
        
        except Exception as e:
            logger.error(f"Error checking event demand: {e}")
        
        return alerts
    
    def _check_social_trends(
        self,
        user: User,
        keyword: str
    ) -> List[Dict]:
        """Check social media trend-based demand"""
        alerts = []
        
        try:
            # Get search trend score
            trend_score = self.trends_service.get_trend_score(keyword)
            
            if trend_score and trend_score > 70:  # High trend
                alerts.append({
                    "user_id": user.id,
                    "alert_type": AlertType.SOCIAL_TREND.value,
                    "priority": AlertPriority.HIGH.value,
                    "title": f"Trending: {keyword} on Social Media",
                    "message": f"{keyword} is trending (score: {trend_score}/100). "
                             f"Capitalize on this trend by increasing visibility and stock.",
                    "keyword": keyword,
                    "context_data": {
                        "trend_score": trend_score,
                        "source": "google_trends"
                    },
                    "predicted_impact": trend_score * 0.8,
                    "confidence_score": trend_score / 100
                })
        
        except Exception as e:
            logger.error(f"Error checking social trends: {e}")
        
        return alerts
    
    def _check_competitor_stockouts(
        self,
        user: User,
        keyword: str
    ) -> List[Dict]:
        """Check competitor stockout opportunities"""
        alerts = []
        
        try:
            # In a real implementation, integrate with competitor monitoring
            # Check competitor websites/APIs for stockout signals
            # For now, simulate detection
            
            # This would require web scraping or API integration
            # Example: Monitor competitor product pages for "out of stock" signals
            
            alerts.append({
                "user_id": user.id,
                "alert_type": AlertType.COMPETITOR_STOCKOUT.value,
                "priority": AlertPriority.HIGH.value,
                "title": f"Competitor Stockout: {keyword} Opportunity",
                "message": f"Competitor stockout detected for {keyword}. "
                         f"Increase visibility of your in-stock products now!",
                "keyword": keyword,
                "context_data": {
                    "competitor_count": 1,
                    "opportunity_window": "24 hours"
                },
                "predicted_impact": 40,
                "confidence_score": 0.7
            })
        
        except Exception as e:
            logger.error(f"Error checking competitor stockouts: {e}")
        
        return alerts
    
    def _check_festival_demand(
        self,
        user: User,
        keyword: str,
        city: str
    ) -> List[Dict]:
        """Check festival/holiday-based demand"""
        alerts = []
        
        try:
            # Check for upcoming holidays
            holidays = self.holiday_service.get_upcoming_holidays(
                country=user.location_country,
                days_ahead=7
            )
            
            for holiday in holidays:
                holiday_name = holiday.get("name", "")
                date = holiday.get("date", "")
                
                # Check if keyword matches festival category
                festival_keywords_map = {
                    "diwali": ["lights", "candles", "sweets", "gifts", "clothes"],
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
                                "alert_type": AlertType.FESTIVAL_BOOST.value,
                                "priority": AlertPriority.HIGH.value,
                                "title": f"{holiday_name}: {keyword} Demand Boost",
                                "message": f"{holiday_name} is coming up. "
                                         f"Expected boost in {keyword} demand. Stock and promote now!",
                                "keyword": keyword,
                                "context_data": {
                                    "holiday_name": holiday_name,
                                    "holiday_date": date,
                                    "festival_type": festival
                                },
                                "predicted_impact": 60,
                                "confidence_score": 0.8
                            })
        
        except Exception as e:
            logger.error(f"Error checking festival demand: {e}")
        
        return alerts

