# backend/api/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from data.database import get_session
from data.models import Campaign, Product, ContentAsset
from backend.services.campaign_service import CampaignService
from pydantic import BaseModel

router = APIRouter()

class CampaignCreate(BaseModel):
    product_id: UUID
    name: str
    description: Optional[str] = None
    channel: str
    customer_segment: Optional[str] = None
    frequency: str = "daily"
    budget: float

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None

class CampaignResponse(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    name: str
    description: Optional[str]
    channel: str
    customer_segment: Optional[str]
    frequency: Optional[str]
    budget: float
    status: str
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    session: Session = Depends(get_session),
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=100)
):
    """List all campaigns with optional filters"""
    query = select(Campaign)
    
    if channel:
        query = query.where(Campaign.channel == channel)
    if status:
        query = query.where(Campaign.status == status)
    
    query = query.limit(limit)
    campaigns = session.exec(query).all()
    
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    session: Session = Depends(get_session)
):
    """Get a specific campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: Session = Depends(get_session)
):
    """Create a new campaign"""
    # Verify product exists
    product = session.get(Product, campaign_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create campaign
    campaign = Campaign(
        product_id=campaign_data.product_id,
        name=campaign_data.name,
        description=campaign_data.description,
        channel=campaign_data.channel,
        customer_segment=campaign_data.customer_segment,
        frequency=campaign_data.frequency,
        budget=campaign_data.budget,
        status="draft"
    )
    
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return campaign

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_update: CampaignUpdate,
    session: Session = Depends(get_session)
):
    """Update a campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update fields
    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return campaign

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete a campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    session.delete(campaign)
    session.commit()
    
    return {"message": "Campaign deleted successfully"}

@router.post("/{campaign_id}/activate", response_model=CampaignResponse)
async def activate_campaign(
    campaign_id: UUID,
    session: Session = Depends(get_session)
):
    """Activate a campaign"""
    service = CampaignService(session)
    campaign = await service.activate_campaign(campaign_id)
    
    return campaign

@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: UUID,
    session: Session = Depends(get_session)
):
    """Pause a campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.status = "paused"
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return campaign

@router.get("/{campaign_id}/content", response_model=List[ContentAsset])
async def get_campaign_content(
    campaign_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all content assets for a campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign.content_assets