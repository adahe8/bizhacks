# backend/api/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import json

from data.database import get_session
from data.models import Campaign, CampaignStatus, CompanyDetails, CustomerSegment
from backend.services.campaign_service import CampaignService
from pydantic import BaseModel

router = APIRouter()

class CampaignCreate(BaseModel):
    name: str
    description: str
    channel: str
    segment_id: int
    frequency_days: int
    assigned_budget: float
    theme: Optional[str] = None
    strategy: Optional[str] = None

class CampaignUpdate(BaseModel):
    status: Optional[CampaignStatus] = None
    assigned_budget: Optional[float] = None
    frequency_days: Optional[int] = None

class CompanySetup(BaseModel):
    product_name: str
    product_description: str
    firm_name: str
    firm_details: str
    market_details: str
    strategic_goals: str
    monthly_budget: float
    guardrails: str
    rebalancing_frequency_days: int = 7
    max_campaigns_to_generate: int = 10

@router.post("/setup")
async def setup_company(setup_data: CompanySetup, session: Session = Depends(get_session)):
    """Initial company setup"""
    # Check if company already exists
    existing = session.exec(select(CompanyDetails)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already setup")
    
    company = CompanyDetails(**setup_data.dict())
    session.add(company)
    session.commit()
    session.refresh(company)
    
    return {"message": "Company setup complete", "company_id": company.id}

@router.post("/upload-firm-pdf")
async def upload_firm_pdf(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """Upload and process firm details PDF"""
    # In a real implementation, this would process the PDF
    # For now, we'll simulate extraction
    content = await file.read()
    
    # Simulated extraction
    extracted_text = f"Extracted from {file.filename}: Company overview and details..."
    
    return {"extracted_text": extracted_text}

@router.get("/", response_model=List[Campaign])
async def list_campaigns(
    status: Optional[CampaignStatus] = None,
    channel: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all campaigns with optional filters"""
    query = select(Campaign)
    
    if status:
        query = query.where(Campaign.status == status)
    if channel:
        query = query.where(Campaign.channel == channel)
    
    campaigns = session.exec(query).all()
    return campaigns

@router.post("/", response_model=Campaign)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: Session = Depends(get_session)
):
    """Create a new campaign"""
    campaign = Campaign(**campaign_data.dict())
    campaign.current_budget = campaign.assigned_budget
    
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return campaign

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: int, session: Session = Depends(get_session)):
    """Get a specific campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.patch("/{campaign_id}")
async def update_campaign(
    campaign_id: int,
    update_data: CampaignUpdate,
    session: Session = Depends(get_session)
):
    """Update campaign details"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(campaign, key, value)
    
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    
    return campaign

@router.post("/{campaign_id}/approve")
async def approve_campaign(campaign_id: int, session: Session = Depends(get_session)):
    """Approve a campaign for execution"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.status = CampaignStatus.APPROVED
    campaign.updated_at = datetime.utcnow()
    
    session.add(campaign)
    session.commit()
    
    return {"message": "Campaign approved", "campaign_id": campaign_id}