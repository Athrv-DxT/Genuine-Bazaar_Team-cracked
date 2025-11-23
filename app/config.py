"""
Configuration settings for Genuine Bazaar
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = "Genuine Bazaar"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./genuine_bazaar.db"
    )
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # External API Keys
    openweather_api_key: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    calendarific_api_key: Optional[str] = os.getenv("CALENDARIFIC_API_KEY")
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    
    # CORS
    cors_origins: list = ["*"]  # Configure for production
    
    # Data Collection
    data_collection_interval_hours: int = 6
    alert_check_interval_minutes: int = 30
    
    # ML Model
    ml_model_path: str = "ml/model.pkl"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
