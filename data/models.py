# data/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID, uuid4
import json

class Company(SQLModel, table=True):
    """Company model"""
    __tablename__ = "companies"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_name: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None)
    brand_voice: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    products: List["Product"] = Relationship(back_populates="company")

class Product(SQLModel, table=True):
    """Product model"""
    __tablename__ = "products"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: Optional[UUID] = Field(default=None, foreign_key="companies.id")
    product_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    launch_date: Optional[date] = Field(default=None)
    target_skin_type: Optional[str] = Field(default=None)
    
    # Relationships
    company: Optional[Company] = Relationship(back_populates="products")
    campaigns: List["Campaign"] = Relationship(back_populates="product")

class User(SQLModel, table=True):
    """User/Customer model"""
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # Changed to UUID
    age: Optional[int] = Field(default=None)
    location: Optional[str] = Field(default=None)
    skin_type: Optional[str] = Field(default=None)
    channels_engaged: Optional[str] = Field(default=None)  # JSON string
    purchase_history: Optional[str] = Field(default=None)  # JSON string
    
    @property
    def channels_engaged_list(self) -> List[str]:
        if self.channels_engaged:
            return json.loads(self.channels_engaged)
        return []
    
    @property
    def purchase_history_list(self) -> List[dict]:
        if self.purchase_history:
            return json.loads(self.purchase_history)
        return []

class Campaign(SQLModel, table=True):
    """Campaign model"""
    __tablename__ = "campaigns"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    product_id: Optional[UUID] = Field(default=None, foreign_key="products.id")
    name: str
    description: Optional[str] = Field(default=None)
    channel: str  # facebook, email, google_seo
    customer_segment: Optional[str] = Field(default=None)
    frequency: Optional[str] = Field(default=None)  # daily, weekly, monthly
    start_date: Optional[datetime] = Field(default=None)  # NEW FIELD
    budget: float = Field(default=0.0)
    status: str = Field(default="draft")  # draft, active, paused, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    product: Optional[Product] = Relationship(back_populates="campaigns")
    content_assets: List["ContentAsset"] = Relationship(back_populates="campaign")
    metrics: List["Metric"] = Relationship(back_populates="campaign")
    schedules: List["Schedule"] = Relationship(back_populates="campaign")

class ContentAsset(SQLModel, table=True):
    """Content Asset model"""
    __tablename__ = "content_assets"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: Optional[UUID] = Field(default=None, foreign_key="campaigns.id")
    platform: Optional[str] = Field(default=None)
    asset_type: Optional[str] = Field(default=None)  # text, image, video
    copy_text: Optional[str] = Field(default=None)
    visual_url: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default="draft")  # draft, approved, published
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    campaign: Optional[Campaign] = Relationship(back_populates="content_assets")

class Metric(SQLModel, table=True):
    """Metrics model"""
    __tablename__ = "metrics"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: Optional[UUID] = Field(default=None, foreign_key="campaigns.id")
    platform: Optional[str] = Field(default=None)
    clicks: Optional[int] = Field(default=0)
    impressions: Optional[int] = Field(default=0)
    engagement_rate: Optional[float] = Field(default=0.0)
    conversion_rate: Optional[float] = Field(default=0.0)
    cpa: Optional[float] = Field(default=0.0)  # Cost per acquisition
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    campaign: Optional[Campaign] = Relationship(back_populates="metrics")

# Additional models for the application

class CustomerSegment(SQLModel, table=True):
    """Customer Segment model"""
    __tablename__ = "customer_segments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    criteria: Optional[str] = Field(default=None)  # JSON string of criteria
    size: Optional[float] = Field(default=0)  # Percentage of total users
    channel_distribution: Optional[str] = Field(default=None)  # JSON string of channel percentages
    cluster_centroid: Optional[str] = Field(default=None)  # JSON string of centroid features
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CampaignMetrics(SQLModel, table=True):
    """Campaign-specific metrics configuration"""
    __tablename__ = "campaign_metrics"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: UUID = Field(foreign_key="campaigns.id", unique=True)
    channel: str
    metrics_config: str  # JSON string with mean/variance for each metric
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Schedule(SQLModel, table=True):
    """Campaign Schedule model"""
    __tablename__ = "schedules"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: UUID = Field(foreign_key="campaigns.id")
    scheduled_time: datetime
    status: str = Field(default="pending")  # pending, executing, completed, failed
    job_id: Optional[str] = Field(default=None)  # APScheduler job ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    campaign: Campaign = Relationship(back_populates="schedules")

class SetupConfiguration(SQLModel, table=True):
    """Application Setup Configuration"""
    __tablename__ = "setup_configurations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    product_id: Optional[UUID] = Field(default=None, foreign_key="products.id")
    company_id: Optional[UUID] = Field(default=None, foreign_key="companies.id")
    market_details: Optional[str] = Field(default=None)  # JSON string
    strategic_goals: Optional[str] = Field(default=None)
    monthly_budget: float = Field(default=0.0)
    guardrails: Optional[str] = Field(default=None)
    rebalancing_frequency: str = Field(default="weekly")  # daily, weekly, monthly
    campaign_count: int = Field(default=5)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GameState(SQLModel, table=True):
    """Game state tracking"""
    __tablename__ = "game_state"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    current_date: datetime = Field(default_factory=datetime.utcnow)
    game_speed: str = Field(default="medium")  # slow, medium, fast
    is_running: bool = Field(default=False)
    total_reach_optimal: float = Field(default=0.0)
    total_reach_non_optimal: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    """Transaction model for user purchases"""
    __tablename__ = "transactions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    product_id: UUID = Field(foreign_key="products.id")
    amount: float
    transaction_date: datetime
    channel: Optional[str] = Field(default=None)
    campaign_id: Optional[UUID] = Field(default=None, foreign_key="campaigns.id")