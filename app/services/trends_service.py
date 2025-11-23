"""
Google Trends service using pytrends
"""
import logging
from typing import Optional
from app.config import settings
from pytrends.request import TrendReq
import time

logger = logging.getLogger(__name__)


class TrendsService:
    """Service for fetching Google Trends data"""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize TrendsService
        
        Args:
            username: Optional Google account username for pytrends
            password: Optional Google account password for pytrends
        """
        self.username = username
        self.password = password
        self.pytrends = None
    
    def _get_pytrends(self) -> TrendReq:
        """Get or create TrendReq instance"""
        if self.pytrends is None:
            try:
                if self.username and self.password:
                    self.pytrends = TrendReq(
                        hl='en-IN',
                        tz=330,  # IST timezone
                        username=self.username,
                        password=self.password
                    )
                else:
                    self.pytrends = TrendReq(hl='en-IN', tz=330)
            except Exception as e:
                logger.error(f"Failed to initialize pytrends: {e}")
                raise
        return self.pytrends
    
    def get_trend_score(self, keyword: str, geo: str = "IN") -> Optional[int]:
        """
        Fetch search trend score for a keyword in a region
        
        Args:
            keyword: Search keyword
            geo: Geographic region code (default: "IN" for India)
        
        Returns:
            Trend score (0-100) or None if failed
        """
        try:
            pytrends = self._get_pytrends()
            
            # Build payload
            pytrends.build_payload([keyword], geo=geo, timeframe='today 3-m')
            
            # Get interest over time
            data = pytrends.interest_over_time()
            
            if data.empty:
                logger.warning(f"No trend data found for keyword: {keyword}")
                return None
            
            # Get the most recent value (last row, first column)
            latest_score = int(data[keyword].iloc[-1])
            
            logger.info(f"Trend score for '{keyword}': {latest_score}")
            return latest_score
            
        except Exception as e:
            logger.error(f"Error fetching trend score for '{keyword}': {e}")
            return None
        finally:
            # Rate limiting: pytrends recommends delays between requests
            time.sleep(1)
    
    def get_trend_scores_batch(self, keywords: list, geo: str = "IN") -> dict[str, Optional[int]]:
        """
        Fetch trend scores for multiple keywords
        
        Args:
            keywords: List of keywords
            geo: Geographic region code
        
        Returns:
            Dictionary mapping keywords to scores
        """
        results = {}
        for keyword in keywords:
            results[keyword] = self.get_trend_score(keyword, geo)
            time.sleep(2)  # Rate limiting between keywords
        return results

