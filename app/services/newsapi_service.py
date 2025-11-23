import logging
import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"


class NewsAPIService:
    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_API_KEY") or os.getenv("newsapi_key") or None
        self.base_url = NEWSAPI_BASE_URL
    
    def search_trend(self, keyword: str, days: int = 7) -> Optional[Dict]:
        """
        Search for news articles about a keyword and calculate trend score
        
        Args:
            keyword: Search keyword
            days: Number of days to look back (default: 7)
        
        Returns:
            Dictionary with keyword, score, articles count, or None if failed
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured, using fallback")
            return self._get_fallback_score(keyword)
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                "q": keyword,
                "from": from_date,
                "to": to_date,
                "sortBy": "popularity",
                "language": "en",
                "apiKey": self.api_key,
                "pageSize": 100
            }
            
            resp = requests.get(self.base_url, params=params, timeout=10)
            
            if resp.status_code == 401:
                logger.error("NewsAPI: Invalid API key")
                return self._get_fallback_score(keyword)
            
            if resp.status_code == 429:
                logger.warning("NewsAPI: Rate limit exceeded")
                return self._get_fallback_score(keyword)
            
            resp.raise_for_status()
            data = resp.json()
            
            total_articles = data.get("totalResults", 0)
            
            if total_articles == 0:
                logger.info(f"No news articles found for '{keyword}'")
                return {
                    "keyword": keyword,
                    "score": 0,
                    "articles": 0,
                    "status": "none",
                    "source": "newsapi"
                }
            
            score = self._calculate_score(total_articles, days)
            
            logger.info(f"NewsAPI: '{keyword}' - {total_articles} articles, score: {score}")
            
            return {
                "keyword": keyword,
                "score": score,
                "articles": total_articles,
                "status": "trending" if score > 50 else "rising" if score > 20 else "low",
                "source": "newsapi"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request error for '{keyword}': {e}")
            return self._get_fallback_score(keyword)
        except Exception as e:
            logger.error(f"Error in NewsAPI search for '{keyword}': {e}")
            return self._get_fallback_score(keyword)
    
    def _calculate_score(self, article_count: int, days: int) -> int:
        """
        Calculate trend score (0-100) based on article count
        
        More articles = higher score
        Normalized for the time period
        """
        articles_per_day = article_count / days
        
        if articles_per_day >= 50:
            return min(100, 80 + int((articles_per_day - 50) / 2))
        elif articles_per_day >= 20:
            return min(80, 50 + int((articles_per_day - 20) * 1))
        elif articles_per_day >= 10:
            return min(50, 30 + int((articles_per_day - 10) * 2))
        elif articles_per_day >= 5:
            return min(30, 15 + int((articles_per_day - 5) * 3))
        elif articles_per_day >= 1:
            return min(15, 5 + int(articles_per_day * 2))
        else:
            return max(0, int(articles_per_day * 5))
    
    def _get_fallback_score(self, keyword: str) -> Dict:
        """
        Fallback when NewsAPI is not available
        Uses keyword analysis to estimate trend
        """
        keyword_lower = keyword.lower()
        
        high_trend_keywords = {
            "iphone": 85, "samsung": 80, "apple": 90, "google": 85,
            "crypto": 75, "bitcoin": 80, "ai": 90, "chatgpt": 85,
            "tesla": 80, "amazon": 85, "netflix": 75, "meta": 70
        }
        
        medium_trend_keywords = {
            "laptop": 60, "smartphone": 65, "headphones": 55,
            "cake": 50, "pizza": 55, "coffee": 70, "restaurant": 60,
            "fashion": 65, "clothes": 60, "shoes": 65, "makeup": 55
        }
        
        if keyword_lower in high_trend_keywords:
            score = high_trend_keywords[keyword_lower]
        elif keyword_lower in medium_trend_keywords:
            score = medium_trend_keywords[keyword_lower]
        else:
            score = 30
        
        return {
            "keyword": keyword,
            "score": score,
            "articles": 0,
            "status": "trending" if score > 50 else "rising" if score > 20 else "low",
            "source": "estimated"
        }

