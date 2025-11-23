import logging
from typing import Dict, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class LangChainSearchService:
    def __init__(self):
        self.gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.google_trends_fallback = True
    
    def _normalize_keyword(self, keyword: str) -> str:
        keyword = keyword.strip().lower()
        keyword_mappings = {
            "cake": "cake dessert",
            "laptop": "laptop computer",
            "phone": "smartphone",
            "tv": "television",
            "t-shirt": "tshirt",
            "t shirt": "tshirt"
        }
        return keyword_mappings.get(keyword, keyword)
    
    def _get_gdelt_score(self, keyword: str) -> Optional[int]:
        try:
            params = {
                "query": keyword,
                "mode": "timelinevolinfo",
                "format": "json"
            }
            resp = requests.get(self.gdelt_url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "timeline" in data and isinstance(data["timeline"], list) and len(data["timeline"]) > 0:
                    item = data["timeline"][0]
                    if isinstance(item, dict) and "data" in item:
                        data_list = item["data"]
                        if isinstance(data_list, list) and len(data_list) > 0:
                            values = [d.get("value", 0) for d in data_list if isinstance(d, dict) and d.get("value", 0) > 0]
                            if values and len(values) >= 7:
                                recent_val = values[-1]
                                max_val = max(values)
                                if max_val > 0.03 and recent_val > 0.005:
                                    if recent_val < 10:
                                        score = min(100, max(10, int(recent_val * 100)))
                                    else:
                                        score = min(100, max(10, int(recent_val)))
                                    return score
        except Exception as e:
            logger.debug(f"GDELT error for {keyword}: {e}")
        return None
    
    def _get_estimated_score(self, keyword: str) -> int:
        keyword_lower = keyword.lower()
        
        popular_keywords = {
            "smartphone": 85, "laptop": 75, "headphones": 70, "tablet": 65,
            "cake": 60, "pizza": 70, "burger": 65, "coffee": 80,
            "t-shirt": 70, "jeans": 75, "shoes": 80, "dress": 65,
            "lipstick": 60, "perfume": 55, "skincare": 70,
            "furniture": 50, "sofa": 55, "bed": 60
        }
        
        if keyword_lower in popular_keywords:
            return popular_keywords[keyword_lower]
        
        if any(word in keyword_lower for word in ["phone", "mobile", "smart"]):
            return 70
        if any(word in keyword_lower for word in ["food", "eat", "restaurant"]):
            return 60
        if any(word in keyword_lower for word in ["cloth", "wear", "fashion"]):
            return 65
        if any(word in keyword_lower for word in ["beauty", "makeup", "cosmetic"]):
            return 55
        
        return 40
    
    def search(self, keyword: str, country: str = "IN") -> Dict:
        keyword = keyword.strip()
        if len(keyword) < 3:
            return {
                "keyword": keyword,
                "trend_score": 0,
                "status": "none",
                "source": "invalid",
                "error": "Keyword must be at least 3 characters"
            }
        
        normalized = self._normalize_keyword(keyword)
        
        gdelt_score = self._get_gdelt_score(normalized)
        
        if gdelt_score and gdelt_score >= 10:
            return {
                "keyword": keyword,
                "trend_score": gdelt_score,
                "status": "trending" if gdelt_score > 50 else "rising",
                "source": "gdelt"
            }
        
        estimated_score = self._get_estimated_score(keyword)
        
        return {
            "keyword": keyword,
            "trend_score": estimated_score,
            "status": "trending" if estimated_score > 50 else "rising",
            "source": "estimated"
        }

