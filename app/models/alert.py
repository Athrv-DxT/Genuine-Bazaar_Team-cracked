"""
Alert and notification models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class AlertType(str, enum.Enum):
    """Types of alerts"""
    DEMAND_PEAK = "demand_peak"
    WEATHER_OPPORTUNITY = "weather_opportunity"
    EVENT_SPIKE = "event_spike"
    SOCIAL_TREND = "social_trend"
    COMPETITOR_STOCKOUT = "competitor_stockout"
    FESTIVAL_BOOST = "festival_boost"
    PROMOTION_TIMING = "promotion_timing"
    SENTIMENT_PEAK = "sentiment_peak"
    FOOTFALL_WINDOW = "footfall_window"


class AlertPriority(str, enum.Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AlertStatus(str, enum.Enum):
    """Alert status"""
    NEW = "new"
    READ = "read"
    ACTED = "acted"
    DISMISSED = "dismissed"


class Alert(Base):
    """Alert/notification for retailers"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # AlertType enum value
    priority = Column(String(20), default=AlertPriority.MEDIUM.value)
    status = Column(String(20), default=AlertStatus.NEW.value)
    
    # Alert content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    keyword = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)
    
    # Context data
    context_data = Column(JSON, default=dict)  # Additional context (weather, events, etc.)
    predicted_impact = Column(Float, nullable=True)  # Predicted revenue impact
    confidence_score = Column(Float, default=0.0)  # 0.0-1.0
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime, nullable=True)
    acted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(user_id={self.user_id}, type={self.alert_type}, priority={self.priority})>"


class DemandSignal(Base):
    """Historical demand signals for analysis"""
    __tablename__ = "demand_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    city = Column(String(100), nullable=False, index=True)
    keyword = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    
    # Signal data
    search_trend_score = Column(Integer, nullable=True)  # 0-100
    temperature = Column(Float, nullable=True)
    rain_probability = Column(Float, nullable=True)
    is_holiday = Column(Boolean, default=False)
    holiday_name = Column(String(200), nullable=True)
    
    # Social media signals
    social_mention_count = Column(Integer, default=0)
    social_sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    
    # Event data
    local_events = Column(JSON, default=list)
    competitor_stockouts = Column(JSON, default=list)
    
    # Composite index
    __table_args__ = (
        {'extend_existing': True},
    )
    
    def __repr__(self):
        return f"<DemandSignal(city={self.city}, keyword={self.keyword}, timestamp={self.timestamp})>"

