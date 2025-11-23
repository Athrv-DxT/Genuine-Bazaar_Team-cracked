"""
Trends and industry-specific routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_active_user
from app.models.user import User
from app.services.industry_trends import IndustryTrendsService
from app.services.gdelt_service import GDELTService

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/industry/{industry}")
async def get_industry_trends(
    industry: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current trends for a specific industry"""
    trends_service = IndustryTrendsService()
    location = current_user.location_country or "IN"
    
    if industry.lower() == "clothes":
        trends = trends_service.get_clothing_trends(location)
    else:
        trends = trends_service.get_industry_trends(industry, location)
    
    return {
        "industry": industry,
        "location": location,
        "trends": trends,
        "count": len(trends)
    }


@router.get("/my-industries")
async def get_my_industry_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trends for all user's market categories"""
    trends_service = IndustryTrendsService()
    location = current_user.location_country or "IN"
    
    # If no categories, use default categories
    categories = current_user.market_categories or ["electronics", "clothes", "food"]
    
    all_trends = trends_service.get_all_industry_trends(
        categories,
        location
    )
    
    # Ensure we always have trends
    if not all_trends or len(all_trends) == 0:
        # Add default trends for common categories
        default_categories = ["electronics", "clothes", "food"]
        all_trends = trends_service.get_all_industry_trends(default_categories, location)
    
    return {
        "user_industries": categories,
        "location": location,
        "trends": all_trends,
        "total_trends": sum(len(t) for t in all_trends.values())
    }


@router.get("/clothing")
async def get_clothing_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current clothing/fashion trends"""
    trends_service = IndustryTrendsService()
    location = current_user.location_country or "IN"
    
    trends = trends_service.get_clothing_trends(location)
    
    return {
        "industry": "clothes",
        "location": location,
        "trends": trends,
        "count": len(trends)
    }


@router.get("/search")
async def search_keyword_trends(
    keyword: str = Query(..., description="Keyword to search for trends"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    gdelt_service = GDELTService()
    location = current_user.location_country or "IN"
    
    if len(keyword.strip()) < 3:
        raise HTTPException(status_code=400, detail="Keyword must be at least 3 characters")
    
    result = gdelt_service.search_keyword(keyword, country=location)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"No genuine trend data found for '{keyword}'. The keyword may not be trending or may not exist in news sources."
        )
    
    return {
        "keyword": keyword,
        "location": location,
        "trend_score": result.get("trend_score", 0),
        "status": result.get("status", "rising"),
        "source": result.get("source", "gdelt")
    }
