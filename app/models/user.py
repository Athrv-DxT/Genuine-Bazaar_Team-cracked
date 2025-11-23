"""
User and retailer models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MarketCategory(str, enum.Enum):
    """Market categories for retailers"""
    ELECTRONICS = "electronics"
    CLOTHES = "clothes"
    FOOD = "food"
    BEAUTY = "beauty"
    HOME = "home"
    SPORTS = "sports"
    BOOKS = "books"
    TOYS = "toys"
    AUTOMOTIVE = "automotive"
    OTHER = "other"


class User(Base):
    """User/Retailer model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Retailer-specific fields
    business_name = Column(String(255), nullable=True)
    market_categories = Column(JSON, default=list)  # List of MarketCategory values
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(100), nullable=True)
    location_country = Column(String(100), default="IN")
    
    # Preferences
    alert_preferences = Column(JSON, default=lambda: {})  # Alert settings
    notification_email = Column(String(255), nullable=True)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    tracked_keywords = relationship("TrackedKeyword", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email={self.email}, business={self.business_name})>"


class TrackedKeyword(Base):
    """Keywords/categories tracked by user"""
    __tablename__ = "tracked_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyword = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)  # Product category
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tracked_keywords")
    
    def __repr__(self):
        return f"<TrackedKeyword(user_id={self.user_id}, keyword={self.keyword})>"

