"""
Configuration settings for CryptoAnalyzer Pro
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "CryptoAnalyzer Pro"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://crypto_user:crypto_pass@postgres:5432/crypto_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # External APIs
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: Optional[str] = None
    
    # Rate Limiting
    API_RATE_LIMIT: int = 50  # requests per minute
    API_RATE_WINDOW: int = 60  # seconds
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    # Alerts
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Technical Analysis
    DEFAULT_TIMEFRAME: str = "1d"
    MAX_HISTORICAL_DAYS: int = 365
    
    # Scheduler
    SCHEDULER_INTERVAL: int = 300  # 5 minutes
    MARKET_DATA_INTERVAL: int = 60  # 1 minute
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

