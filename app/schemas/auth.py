"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import MarketCategory


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str
    full_name: str
    business_name: Optional[str] = None
    market_categories: List[str] = []  # List of MarketCategory values
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: str = "IN"


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    full_name: str
    business_name: Optional[str]
    market_categories: List[str]
    location_city: Optional[str]
    location_state: Optional[str]
    location_country: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


