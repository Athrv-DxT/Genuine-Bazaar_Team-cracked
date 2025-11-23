"""
GDELT API service for fetching real-time news trends
"""
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

GDELT_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class GDELTService:
    """Service for fetching trends from GDELT API"""
    
    def __init__(self):
        self.base_url = GDELT_BASE_URL
    
    def fetch_gdelt_trends(
        self,
        keyword: str,
        country: str = "IN",
        mode: str = "timelinevolinfo"
    ) -> Optional[Dict]:
        """
        Fetch news volume over time for a keyword using GDELT.
        Returns parsed JSON or None on error.
        """
        params = {
            # what you are searching for; use quotes for phrase, AND/OR for logic
            "query": f'"{keyword}" AND {country}',
            # mode=timelinevolinfo gives you volume over time (good for trends)
            "mode": mode,
            "format": "json"   # important – otherwise you get CSV/plain text
        }
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"GDELT data fetched for keyword: {keyword}")
            return data
        except requests.exceptions.Timeout:
            logger.error(f"GDELT API timeout for keyword: {keyword}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling GDELT for {keyword}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error with GDELT for {keyword}: {e}")
            return None
    
    def get_trend_score(
        self,
        keyword: str,
        country: str = "IN"
    ) -> Optional[int]:
        """
        Get trend score (0-100) for a keyword based on GDELT news volume.
        
        Args:
            keyword: Search keyword
            country: Country code (default: "IN" for India)
        
        Returns:
            Trend score (0-100) or None if failed
        """
        try:
            data = self.fetch_gdelt_trends(keyword, country)
            
            if not data:
                return None
            
            # Parse timelinevolinfo response
            # The response structure can vary, try multiple formats
            score = None
            
            # Format 1: {"timeline": [{"datetime": "...", "value": ...}, ...]}
            if "timeline" in data and isinstance(data["timeline"], list):
                if len(data["timeline"]) > 0:
                    # Get the most recent value
                    latest = data["timeline"][-1]
                    if isinstance(latest, dict):
                        volume = latest.get("value") or latest.get("Volume") or latest.get("volume", 0)
                        if volume:
                            score = min(100, max(10, int(volume)))  # Minimum 10 to show it's trending
            
            # Format 2: {"data": [{"value": ...}, ...]}
            if score is None and "data" in data:
                data_list = data["data"]
                if isinstance(data_list, list) and len(data_list) > 0:
                    latest = data_list[-1]
                    if isinstance(latest, dict):
                        volume = latest.get("value") or latest.get("Volume") or latest.get("volume", 0)
                        if volume:
                            score = min(100, max(10, int(volume)))
            
            # Format 3: Direct array response
            if score is None and isinstance(data, list) and len(data) > 0:
                latest = data[-1]
                if isinstance(latest, dict):
                    volume = latest.get("value") or latest.get("Volume") or latest.get("volume", 0)
                    if volume:
                        score = min(100, max(10, int(volume)))
            
            # If we still don't have a score, check if there's any volume data
            if score is None:
                # Try to find any numeric value that might represent volume
                import json
                data_str = json.dumps(data)
                # If response has any data, give it a baseline score
                if data and len(str(data)) > 10:  # Non-empty response
                    score = 30  # Baseline score for any GDELT response
                    logger.info(f"GDELT returned data for '{keyword}', using baseline score")
            
            if score:
                logger.info(f"GDELT trend score for '{keyword}': {score}")
                return score
            
            logger.warning(f"No valid trend score extracted for keyword: {keyword}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting trend score from GDELT for '{keyword}': {e}")
            return None
    
    def get_trends_for_keywords(
        self,
        keywords: List[str],
        country: str = "IN"
    ) -> List[Dict]:
        """
        Get trends for multiple keywords using GDELT.
        
        Args:
            keywords: List of keywords to check
            country: Country code
        
        Returns:
            List of trend dictionaries with keyword, trend_score, status
        """
        trends = []
        
        for keyword in keywords:
            try:
                score = self.get_trend_score(keyword, country)
                
                if score is not None and score > 0:
                    trends.append({
                        "keyword": keyword,
                        "trend_score": score,
                        "status": "trending" if score > 50 else "rising",
                        "source": "gdelt"
                    })
            except Exception as e:
                logger.error(f"Error processing keyword {keyword}: {e}")
                continue
        
        # Sort by trend score
        trends.sort(key=lambda x: x["trend_score"], reverse=True)
        
        return trends
    
    def search_keyword(
        self,
        keyword: str,
        country: str = "IN"
    ) -> Optional[Dict]:
        """
        Search for a specific keyword and return detailed trend data.
        
        Args:
            keyword: Keyword to search
            country: Country code
        
        Returns:
            Dictionary with trend information or None
        """
        try:
            data = self.fetch_gdelt_trends(keyword, country)
            
            if not data:
                return None
            
            score = self.get_trend_score(keyword, country)
            
            if score is None:
                return None
            
            return {
                "keyword": keyword,
                "trend_score": score,
                "status": "trending" if score > 50 else "rising",
                "source": "gdelt",
                "country": country,
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"Error searching keyword {keyword}: {e}")
            return None

