from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "BizHacks Marketing Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Keys
    GEMINI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./campaign.db"
    
    # External APIs
    FACEBOOK_API_ENDPOINT: str = "http://localhost:8000/mock/facebook"
    GOOGLE_ADS_API_ENDPOINT: str = "http://localhost:8000/mock/google"
    EMAIL_SERVICE_API_ENDPOINT: str = "http://localhost:8000/mock/email"
    
    FACEBOOK_API_KEY: Optional[str] = None
    GOOGLE_ADS_API_KEY: Optional[str] = None
    EMAIL_SERVICE_API_KEY: Optional[str] = None
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "UTC"
    SCHEDULER_JOB_DEFAULTS_COALESCE: bool = True
    SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES: int = 3
    SCHEDULER_MISFIRE_GRACE_TIME: int = 30
    
    # Campaign Execution
    MAX_CONCURRENT_CAMPAIGNS: int = 10
    CAMPAIGN_RETRY_ATTEMPTS: int = 3
    CAMPAIGN_RETRY_DELAY: int = 60
    
    # Metrics
    METRICS_REFRESH_INTERVAL: int = 3600  # 1 hour
    METRICS_RETENTION_DAYS: int = 90
    
    # Agent Settings
    AGENT_MAX_RETRIES: int = 3
    AGENT_TIMEOUT: int = 300
    COMPLIANCE_MAX_ITERATIONS: int = 5
    
    # Budget Management
    MIN_CAMPAIGN_BUDGET: float = 100.0
    MAX_BUDGET_ALLOCATION_PERCENT: float = 50.0
    REBALANCING_THRESHOLD: float = 0.15
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()