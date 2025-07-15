from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from data.database import get_session
from data.models import CustomerSegment, Campaign, SetupConfiguration
from agents.segmentation_agent import generate_customer_segments
from agents.campaign_creation_agent import generate_campaign_ideas
from agents.orchestrator_agent import rebalance_budgets
import json

router = APIRouter()

class SegmentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    criteria: Optional[str]
    size: Optional[int]

class CampaignIdea(BaseModel):
    name: str
    description: str
    channel: str
    customer_segment: str
    suggested_budget: float
    frequency: str

class CampaignGenerationRequest(BaseModel):
    segments: List[str]
    channels: List[str] = ["facebook", "email", "google_seo"]

class BudgetRebalanceResponse(BaseModel):
    campaign_id: UUID
    old_budget: float
    new_budget: float
    reason: str

@router.post("/segment")
async def create_customer_segments(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Generate customer segments based on setup configuration"""
    # Get active setup
    setup = session.exec(
        select(SetupConfiguration).where(SetupConfiguration.is_active == True)
    ).first()
    
    if not setup:
        raise HTTPException(status_code=400, detail="No active setup configuration found")
    
    # Generate segments
    try:
        segments = await generate_customer_segments(
            product_id=str(setup.product_id),
            market_details=json.loads(setup.market_details) if setup.market_details else {},
            strategic_goals=setup.strategic_goals
        )
        
        # Save segments to database
        saved_segments = []
        for segment in segments:
            db_segment = CustomerSegment(
                name=segment["name"],
                description=segment["description"],
                criteria=json.dumps(segment["criteria"]),
                size=segment.get("size", 0)
            )
            session.add(db_segment)
            saved_segments.append(db_segment)
        
        session.commit()
        
        return {
            "message": "Customer segments generated successfully",
            "segments": [
                SegmentResponse(
                    id=seg.id,
                    name=seg.name,
                    description=seg.description,
                    criteria=seg.criteria,
                    size=seg.size
                )
                for seg in saved_segments
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating segments: {str(e)}")

@router.get("/segments", response_model=List[SegmentResponse])
async def get_customer_segments(session: Session = Depends(get_session)):
    """Get all customer segments"""
    segments = session.exec(select(CustomerSegment)).all()
    return segments

@router.post("/create-campaigns", response_model=List[CampaignIdea])
async def create_campaign_ideas(
    request: CampaignGenerationRequest,
    session: Session = Depends(get_session)
):
    """Generate campaign ideas based on segments and channels"""
    # Get active setup
    setup = session.exec(
        select(SetupConfiguration).where(SetupConfiguration.is_active == True)
    ).first()
    
    if not setup:
        raise HTTPException(status_code=400, detail="No active setup configuration found")
    
    try:
        # Generate campaign ideas
        ideas = await generate_campaign_ideas(
            segments=request.segments,
            channels=request.channels,
            strategic_goals=setup.strategic_goals,
            monthly_budget=setup.monthly_budget,
            campaign_count=setup.campaign_count
        )
        
        return ideas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating campaign ideas: {str(e)}")

@router.post("/rebalance-budgets", response_model=List[BudgetRebalanceResponse])
async def trigger_budget_rebalance(session: Session = Depends(get_session)):
    """Manually trigger budget rebalancing across campaigns"""
    try:
        rebalance_results = await rebalance_budgets()
        
        return [
            BudgetRebalanceResponse(
                campaign_id=result["campaign_id"],
                old_budget=result["old_budget"],
                new_budget=result["new_budget"],
                reason=result["reason"]
            )
            for result in rebalance_results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebalancing budgets: {str(e)}")

@router.post("/execute-campaign/{campaign_id}")
async def execute_campaign_now(
    campaign_id: UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Manually execute a campaign immediately"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign must be active to execute")
    
    # Execute campaign in background
    from services.campaign_service import execute_campaign
    background_tasks.add_task(execute_campaign, str(campaign_id))
    
    return {"message": f"Campaign {campaign.name} execution started"}

@router.post("/validate-content")
async def validate_content(
    content: dict,
    session: Session = Depends(get_session)
):
    """Validate content against brand guardrails"""
    # Get active setup for guardrails
    setup = session.exec(
        select(SetupConfiguration).where(SetupConfiguration.is_active == True)
    ).first()
    
    if not setup:
        raise HTTPException(status_code=400, detail="No active setup configuration found")
    
    from agents.compliance_agent import validate_content
    
    try:
        validation_result = await validate_content(
            content=content,
            guardrails=setup.guardrails
        )
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating content: {str(e)}")