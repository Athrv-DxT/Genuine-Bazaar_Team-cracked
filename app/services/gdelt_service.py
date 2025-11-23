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
    
    def _validate_trend_data(self, data: Dict, keyword: str) -> bool:
        """Validate that the data represents a genuine trending keyword"""
        try:
            if "timeline" not in data:
                return False
            
            timeline = data["timeline"]
            if not isinstance(timeline, list) or len(timeline) == 0:
                return False
            
            item = timeline[0]
            if not isinstance(item, dict) or "data" not in item:
                return False
            
            data_list = item["data"]
            if not isinstance(data_list, list) or len(data_list) < 7:
                return False
            
            values = [d.get("value", 0) for d in data_list if isinstance(d, dict) and d.get("value", 0) > 0]
            
            if len(values) < 7:
                return False
            
            max_val = max(values)
            avg_val = sum(values) / len(values)
            recent_vals = values[-7:]
            recent_avg = sum(recent_vals) / len(recent_vals)
            recent_val = values[-1]
            
            has_min_volume = max_val > 0.05
            has_recent_activity = recent_val > 0.01
            is_above_average = recent_avg >= avg_val * 0.9
            
            is_valid = has_min_volume and has_recent_activity and is_above_average
            
            if not is_valid:
                logger.debug(f"Keyword '{keyword}' failed validation: volume={has_min_volume}, activity={has_recent_activity}, above_avg={is_above_average}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating trend data for '{keyword}': {e}")
            return False
    
    def get_trend_score(
        self,
        keyword: str,
        country: str = "IN"
    ) -> Optional[int]:
        try:
            data = self.fetch_gdelt_trends(keyword, country)
            
            if not data:
                return None
            
            if not self._validate_trend_data(data, keyword):
                logger.info(f"Keyword '{keyword}' did not pass validation - not a genuine trend")
                return None
            
            score = None
            
            if "timeline" in data:
                timeline = data["timeline"]
                if isinstance(timeline, list) and len(timeline) > 0:
                    for item in timeline:
                        if isinstance(item, dict) and "data" in item:
                            data_list = item["data"]
                            if isinstance(data_list, list) and len(data_list) > 0:
                                values = [d.get("value", 0) for d in data_list if isinstance(d, dict) and d.get("value", 0) > 0]
                                if values:
                                    recent_val = values[-1]
                                    recent_avg = sum(values[-7:]) / min(7, len(values))
                                    overall_avg = sum(values) / len(values)
                                    
                                    if recent_val > 0:
                                        if recent_val < 10:
                                            base_score = int(recent_val * 100)
                                        else:
                                            base_score = int(recent_val)
                                        
                                        if recent_avg > overall_avg * 1.1:
                                            score = min(100, max(20, base_score + 20))
                                        elif recent_avg > overall_avg:
                                            score = min(100, max(15, base_score + 10))
                                        else:
                                            score = min(100, max(10, base_score))
                                        
                                        logger.info(f"GDELT extracted value {recent_val:.4f} -> score {score} for '{keyword}'")
                                        break
            
            if score and score >= 10:
                logger.info(f"GDELT trend score for '{keyword}': {score}")
                return score
            
            logger.warning(f"No valid trend score extracted for keyword: {keyword} (score: {score})")
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
                
                if score is not None and score >= 10:
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
                logger.info(f"No data returned for keyword '{keyword}'")
                return None
            
            if not self._validate_trend_data(data, keyword):
                logger.info(f"Keyword '{keyword}' search failed validation")
                return None
            
            score = None
            
            if "timeline" in data:
                timeline = data["timeline"]
                if isinstance(timeline, list) and len(timeline) > 0:
                    for item in timeline:
                        if isinstance(item, dict) and "data" in item:
                            data_list = item["data"]
                            if isinstance(data_list, list) and len(data_list) > 0:
                                values = [d.get("value", 0) for d in data_list if isinstance(d, dict) and d.get("value", 0) > 0]
                                if values:
                                    recent_val = values[-1]
                                    recent_avg = sum(values[-7:]) / min(7, len(values))
                                    overall_avg = sum(values) / len(values)
                                    
                                    if recent_val > 0:
                                        if recent_val < 10:
                                            base_score = int(recent_val * 100)
                                        else:
                                            base_score = int(recent_val)
                                        
                                        if recent_avg > overall_avg * 1.1:
                                            score = min(100, max(20, base_score + 20))
                                        elif recent_avg > overall_avg:
                                            score = min(100, max(15, base_score + 10))
                                        else:
                                            score = min(100, max(10, base_score))
                                        
                                        logger.info(f"GDELT search extracted value {recent_val:.4f} -> score {score} for '{keyword}'")
                                        break
            
            if score is None or score < 10:
                logger.info(f"Keyword '{keyword}' score too low or invalid: {score}")
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
            import traceback
            traceback.print_exc()
            return None
