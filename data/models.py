from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import json


class ChannelType(str, Enum):
    FACEBOOK = "facebook"
    EMAIL = "email"
    GOOGLE_ADS = "google_ads"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class CompanyDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_name: str
    product_description: str
    firm_name: str
    firm_details: str  # Natural language description from PDF or manual input
    market_details: str
    strategic_goals: str
    monthly_budget: float
    guardrails: str  # Brand norms and compliance rules
    rebalancing_frequency_days: int = 7
    max_campaigns_to_generate: int = 10
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerSegment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    characteristics: str  # JSON string of key characteristics
    size_estimate: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    campaigns: List["Campaign"] = Relationship(back_populates="segment")


class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    channel: ChannelType
    segment_id: int = Field(foreign_key="customersegment.id")
    status: CampaignStatus = CampaignStatus.DRAFT
    frequency_days: int  # How often to publish
    assigned_budget: float
    current_budget: float  # Adjusted by orchestrator
    theme: Optional[str] = None
    strategy: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    
    # Relationships
    segment: CustomerSegment = Relationship(back_populates="campaigns")
    contents: List["Content"] = Relationship(back_populates="campaign")
    metrics: List["CampaignMetrics"] = Relationship(back_populates="campaign")


class Content(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    channel: ChannelType
    content_type: str  # "text", "image", "video", etc.
    content_data: str  # JSON string with actual content
    compliance_approved: bool = False
    compliance_notes: Optional[str] = None
    published: bool = False
    published_at: Optional[datetime] = None
    external_id: Optional[str] = None  # ID from external platform
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    campaign: Campaign = Relationship(back_populates="contents")


class CampaignMetrics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    channel: ChannelType
    metric_date: datetime
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    engagement_rate: float = 0.0
    ctr: float = 0.0  # Click-through rate
    cpc: float = 0.0  # Cost per click
    roi: float = 0.0
    custom_metrics: Optional[str] = None  # JSON for channel-specific metrics
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    campaign: Campaign = Relationship(back_populates="metrics")


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    interests: Optional[str] = None  # JSON array of interests
    demographics: Optional[str] = None  # JSON object
    segment_id: Optional[int] = Field(default=None, foreign_key="customersegment.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="customer")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    transaction_date: datetime
    amount: float
    product_id: Optional[str] = None
    channel_attribution: Optional[ChannelType] = None
    campaign_attribution_id: Optional[int] = Field(default=None, foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    customer: Customer = Relationship(back_populates="transactions")


class MarketingMaterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    file_type: str  # "pdf", "image", etc.
    file_path: str
    content_extracted: Optional[str] = None  # Extracted text for inspiration
    # metadata: Optional[str] = None  # JSON metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)