"""
Calendarific API service for Indian holidays and festivals
"""
import logging
from typing import Optional, Tuple
import requests
from datetime import datetime, date

logger = logging.getLogger(__name__)


class HolidayService:
    """Service for fetching holiday data from Calendarific API"""
    
    BASE_URL = "https://calendarific.com/api/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize HolidayService
        
        Args:
            api_key: Calendarific API key (optional, will use from config if not provided)
        """
        from app.config import settings
        self.api_key = api_key or settings.calendarific_api_key
        if not self.api_key:
            logger.warning("Calendarific API key not provided - holiday features will be limited")
    
    def get_holidays(self, country: str = "IN", year: Optional[int] = None) -> Optional[list]:
        """
        Fetch holidays for a country and year
        
        Args:
            country: Country code (default: "IN" for India)
            year: Year (default: current year)
        
        Returns:
            List of holiday dictionaries, or None if failed
        """
        try:
            if year is None:
                year = datetime.now().year
            
            url = f"{self.BASE_URL}/holidays"
            params = {
                "api_key": self.api_key,
                "country": country,
                "year": year
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "response" not in data or "holidays" not in data["response"]:
                logger.warning(f"No holidays data for {country} in {year}")
                return []
            
            holidays = data["response"]["holidays"]
            logger.info(f"Fetched {len(holidays)} holidays for {country} in {year}")
            return holidays
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching holidays: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching holidays: {e}")
            return None
    
    def is_holiday_today(self, country: str = "IN") -> Tuple[bool, Optional[str]]:
        """
        Check if today is a holiday
        
        Args:
            country: Country code
        
        Returns:
            Tuple of (is_holiday: bool, holiday_name: Optional[str])
        """
        try:
            today = date.today()
            holidays = self.get_holidays(country, today.year)
            
            if holidays is None:
                return False, None
            
            # Check if today matches any holiday
            for holiday in holidays:
                holiday_date_str = holiday.get("date", {}).get("iso", "")
                if holiday_date_str:
                    try:
                        holiday_date = datetime.fromisoformat(holiday_date_str.split("T")[0]).date()
                        if holiday_date == today:
                            holiday_name = holiday.get("name", "Unknown Holiday")
                            logger.info(f"Today is a holiday: {holiday_name}")
                            return True, holiday_name
                    except (ValueError, AttributeError):
                        continue
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking if today is holiday: {e}")
            return False, None
    
    def is_holiday_on_date(self, check_date: date, country: str = "IN") -> Tuple[bool, Optional[str]]:
        """
        Check if a specific date is a holiday
        
        Args:
            check_date: Date to check
            country: Country code
        
        Returns:
            Tuple of (is_holiday: bool, holiday_name: Optional[str])
        """
        try:
            holidays = self.get_holidays(country, check_date.year)
            
            if holidays is None:
                return False, None
            
            # Check if the date matches any holiday
            for holiday in holidays:
                holiday_date_str = holiday.get("date", {}).get("iso", "")
                if holiday_date_str:
                    try:
                        holiday_date = datetime.fromisoformat(holiday_date_str.split("T")[0]).date()
                        if holiday_date == check_date:
                            holiday_name = holiday.get("name", "Unknown Holiday")
                            return True, holiday_name
                    except (ValueError, AttributeError):
                        continue
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking holiday on date {check_date}: {e}")
            return False, None
    
    def get_upcoming_holidays(self, country: str = "IN", days_ahead: int = 30) -> list:
        """
        Get upcoming holidays within specified days
        
        Args:
            country: Country code
            days_ahead: Number of days to look ahead
        
        Returns:
            List of holiday dictionaries with name and date
        """
        if not self.api_key:
            return []
        
        try:
            from datetime import date, timedelta
            today = date.today()
            end_date = today + timedelta(days=days_ahead)
            
            holidays = self.get_holidays(country, today.year)
            if holidays is None:
                return []
            
            upcoming = []
            for holiday in holidays:
                holiday_date_str = holiday.get("date", {}).get("iso", "")
                if holiday_date_str:
                    try:
                        holiday_date = datetime.fromisoformat(holiday_date_str.split("T")[0]).date()
                        if today <= holiday_date <= end_date:
                            upcoming.append({
                                "name": holiday.get("name", "Unknown Holiday"),
                                "date": holiday_date_str,
                                "description": holiday.get("description", "")
                            })
                    except (ValueError, AttributeError):
                        continue
            
            # Sort by date
            upcoming.sort(key=lambda x: x["date"])
            return upcoming
            
        except Exception as e:
            logger.error(f"Error getting upcoming holidays: {e}")
            return []

