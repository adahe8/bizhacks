# backend/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
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
    
    # Rebalancing Optimization Parameters
    BUDGET_EVENNESS_PENALTY: float = 0.2  # Penalty for uneven distribution
    PERFORMANCE_WEIGHT: float = 0.7  # Weight for performance in optimization
    EVENNESS_WEIGHT: float = 0.3  # Weight for even distribution
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Game Settings
    GAME_SPEEDS: Dict[str, int] = {
        "slow": 30,    # 30 seconds per day
        "medium": 15,  # 15 seconds per day
        "fast": 5      # 5 seconds per day
    }
    DEFAULT_GAME_SPEED: str = "medium"
    
    # Clustering Settings
    NUM_CLUSTERS: int = 4
    CLUSTER_RANDOM_STATE: int = 42
    
    # Channel Metrics Configuration
    CHANNEL_METRICS: Dict[str, Dict[str, Dict[str, float]]] = {
        "facebook": {
            "engagement_rate": {"base_mean": 0.035, "base_variance": 0.008, "spend_coefficient": 0.00001},
            "click_through_rate": {"base_mean": 0.025, "base_variance": 0.006, "spend_coefficient": 0.000008},
            "conversion_rate": {"base_mean": 0.012, "base_variance": 0.003, "spend_coefficient": 0.000005}
        },
        "email": {
            "open_rate": {"base_mean": 0.22, "base_variance": 0.04, "spend_coefficient": 0.00002},
            "click_rate": {"base_mean": 0.028, "base_variance": 0.007, "spend_coefficient": 0.00001},
            "conversion_rate": {"base_mean": 0.018, "base_variance": 0.004, "spend_coefficient": 0.000007}
        },
        "google_seo": {
            "impressions": {"base_mean": 5000, "base_variance": 1200, "spend_coefficient": 0.8},
            "click_through_rate": {"base_mean": 0.032, "base_variance": 0.009, "spend_coefficient": 0.00001},
            "conversion_rate": {"base_mean": 0.015, "base_variance": 0.0035, "spend_coefficient": 0.000006}
        }
    }
    
    # Campaign-specific metrics variance multipliers (for uniqueness)
    CAMPAIGN_VARIANCE_RANGE: tuple = (0.8, 1.2)  # Random multiplier range for each campaign
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()