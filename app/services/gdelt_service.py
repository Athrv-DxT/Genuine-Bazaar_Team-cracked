import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

GDELT_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class GDELTService:
    def __init__(self):
        self.base_url = GDELT_BASE_URL
    
    def fetch_gdelt_trends(
        self,
        keyword: str,
        country: str = "IN",
        mode: str = "timelinevolinfo"
    ) -> Optional[Dict]:
        if len(keyword) < 3:
            logger.warning(f"Keyword '{keyword}' too short for GDELT")
            return None
            
        params = {
            "query": keyword,
            "mode": mode,
            "format": "json"
        }
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=15)
            resp.raise_for_status()
            
            try:
                data = resp.json()
            except:
                logger.warning(f"GDELT returned non-JSON for {keyword}: {resp.text[:200]}")
                return None
                
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
        try:
            data = self.fetch_gdelt_trends(keyword, country)
            
            if not data:
                return None
            
            score = None
            
            if "timeline" in data:
                timeline = data["timeline"]
                if isinstance(timeline, list) and len(timeline) > 0:
                    for item in timeline:
                        if isinstance(item, dict) and "data" in item:
                            data_list = item["data"]
                            if isinstance(data_list, list) and len(data_list) > 0:
                                latest = data_list[-1]
                                if isinstance(latest, dict):
                                    volume = latest.get("value", 0)
                                    if volume and volume > 0:
                                        score = min(100, max(10, int(volume * 100)))
                                        break
            
            if score is None and "data" in data:
                data_list = data["data"]
                if isinstance(data_list, list) and len(data_list) > 0:
                    latest = data_list[-1]
                    if isinstance(latest, dict):
                        volume = latest.get("value") or latest.get("Volume") or latest.get("volume", 0)
                        if volume and volume > 0:
                            score = min(100, max(10, int(volume * 100) if volume < 1 else int(volume)))
            
            if score is None and isinstance(data, list) and len(data) > 0:
                latest = data[-1]
                if isinstance(latest, dict):
                    volume = latest.get("value") or latest.get("Volume") or latest.get("volume", 0)
                    if volume and volume > 0:
                        score = min(100, max(10, int(volume * 100) if volume < 1 else int(volume)))
            
            if score is None:
                if data and len(str(data)) > 10:
                    score = 30
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
        
        trends.sort(key=lambda x: x["trend_score"], reverse=True)
        
        return trends
    
    def search_keyword(
        self,
        keyword: str,
        country: str = "IN"
    ) -> Optional[Dict]:
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
                "country": country
            }
        except Exception as e:
            logger.error(f"Error searching keyword {keyword}: {e}")
            return None
