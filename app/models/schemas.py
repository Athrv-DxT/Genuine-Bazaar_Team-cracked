"""
Pydantic schemas for Genuine Bazaar data models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ChannelType(str, Enum):
    """Retail channel type"""
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"


class AuthenticityStatus(str, Enum):
    """Product authenticity status"""
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    COUNTERFEIT = "counterfeit"
    UNVERIFIED = "unverified"


class FairnessStatus(str, Enum):
    """Fairness status"""
    FAIR = "fair"
    UNFAIR_PENALTY = "unfair_penalty"
    MANIPULATION_DETECTED = "manipulation_detected"
    COMPETITOR_INTERFERENCE = "competitor_interference"


class Product(BaseModel):
    """Product model"""
    id: Optional[str] = None
    name: str
    sku: str
    seller_id: str
    category: str
    channel: ChannelType
    description: Optional[str] = None
    base_price: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Seller(BaseModel):
    """Seller model"""
    id: Optional[str] = None
    name: str
    email: Optional[str] = None
    channel: ChannelType
    store_location: Optional[str] = None
    online_store_url: Optional[str] = None
    created_at: Optional[datetime] = None


class Sale(BaseModel):
    """Sales transaction model"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    quantity: int
    price: float
    total_amount: float
    channel: ChannelType
    timestamp: datetime
    location: Optional[str] = None
    customer_id: Optional[str] = None


class Review(BaseModel):
    """Product review model"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    content: str
    verified_purchase: bool = False
    reviewer_id: Optional[str] = None
    timestamp: datetime
    authenticity_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_fake: Optional[bool] = None


class PriceHistory(BaseModel):
    """Price history tracking"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    price: float
    competitor_price: Optional[float] = None
    competitor_id: Optional[str] = None
    timestamp: datetime
    channel: ChannelType


class RankingHistory(BaseModel):
    """Search ranking history"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    ranking: int
    search_query: Optional[str] = None
    category: str
    timestamp: datetime
    channel: ChannelType
    visibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ImageMetadata(BaseModel):
    """Image metadata with EXIF data"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    image_url: str
    image_hash: Optional[str] = None
    exif_data: Optional[Dict[str, Any]] = None
    location_verified: bool = False
    timestamp_verified: bool = False
    is_duplicate: bool = False
    duplicate_matches: Optional[List[str]] = None
    authenticity_status: AuthenticityStatus = AuthenticityStatus.UNVERIFIED
    uploaded_at: datetime


class BatchInfo(BaseModel):
    """Product batch information"""
    id: Optional[str] = None
    product_id: str
    batch_number: str
    manufacturing_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    packaging_consistency: Optional[float] = Field(None, ge=0.0, le=1.0)
    variations_detected: bool = False
    notes: Optional[str] = None


class ReturnPattern(BaseModel):
    """Product return pattern analysis"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    return_reason: str
    return_count: int
    total_sales: int
    return_rate: float
    pattern_type: str  # e.g., "not_as_described", "quality_issue", "packaging"
    timestamp: datetime


class CausalInsight(BaseModel):
    """Causal insight from analysis"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    insight_type: str  # e.g., "price_change", "competitor_action", "ranking_drop"
    description: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence: List[Dict[str, Any]]
    impact_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    affected_metric: str  # e.g., "sales", "ranking", "reviews"


class AuthenticityReport(BaseModel):
    """Product authenticity report"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    overall_status: AuthenticityStatus
    image_verification: Dict[str, Any]
    duplicate_detection: Dict[str, Any]
    review_verification: Dict[str, Any]
    batch_consistency: Dict[str, Any]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime
    recommendations: List[str]


class FairnessReport(BaseModel):
    """Seller fairness report"""
    id: Optional[str] = None
    seller_id: str
    product_id: Optional[str] = None
    overall_status: FairnessStatus
    ranking_analysis: Dict[str, Any]
    visibility_penalty_detected: bool
    fake_review_manipulation: bool
    competitor_interference: bool
    platform_penalties: List[Dict[str, Any]]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime
    recommendations: List[str]


class ExperienceReport(BaseModel):
    """Product experience integrity report"""
    id: Optional[str] = None
    product_id: str
    seller_id: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
    packaging_consistency: float = Field(..., ge=0.0, le=1.0)
    batch_variations: List[Dict[str, Any]]
    return_patterns: List[ReturnPattern]
    review_sentiment: Dict[str, Any]
    generated_at: datetime
    recommendations: List[str]


class DiagnosticRequest(BaseModel):
    """Request for diagnostic analysis"""
    product_id: Optional[str] = None
    seller_id: Optional[str] = None
    analysis_type: List[str] = ["causality", "authenticity", "fairness", "experience"]
    time_range_days: int = 30
    include_competitors: bool = True


class DiagnosticResponse(BaseModel):
    """Complete diagnostic response"""
    product_id: str
    seller_id: str
    causal_insights: List[CausalInsight]
    authenticity_report: Optional[AuthenticityReport] = None
    fairness_report: Optional[FairnessReport] = None
    experience_report: Optional[ExperienceReport] = None
    generated_at: datetime
    summary: str




