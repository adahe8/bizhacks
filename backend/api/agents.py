# backend/api/agents.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
import logging
import traceback

from data.database import get_session
from data.models import CustomerSegment, Campaign, SetupConfiguration
from agents.segmentation_agent import generate_customer_segments
from agents.campaign_creation_agent import generate_campaign_ideas
from agents.orchestrator_agent import rebalance_budgets
import json

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    logger.info("=== Starting customer segment generation ===")
    
    try:
        # Get active setup
        logger.debug("Fetching active setup configuration...")
        setup = session.exec(
            select(SetupConfiguration).where(SetupConfiguration.is_active == True)
        ).first()
        
        if not setup:
            logger.error("No active setup configuration found")
            raise HTTPException(status_code=400, detail="No active setup configuration found")
        
        logger.info(f"Found active setup: ID={setup.id}, Product={setup.product_id}, Budget=${setup.monthly_budget}")
        
        # Delete existing segments before generating new ones
        logger.debug("Deleting existing customer segments...")
        existing_segments = session.exec(select(CustomerSegment)).all()
        for segment in existing_segments:
            session.delete(segment)
        session.commit()
        logger.info(f"Deleted {len(existing_segments)} existing segments")
        
        # Generate segments
        logger.info("Calling generate_customer_segments...")
        try:
            segments = await generate_customer_segments(
                product_id=str(setup.product_id),
                market_details=json.loads(setup.market_details) if setup.market_details else {},
                strategic_goals=setup.strategic_goals or ""
            )
            
            logger.info(f"Generated {len(segments)} segments from segmentation agent")
            
            # Save segments to database
            saved_segments = []
            for i, segment in enumerate(segments):
                logger.debug(f"Processing segment {i+1}: {segment.get('name', 'Unknown')}")
                
                # Extract segment data
                segment_name = segment.get("name", f"Segment {i+1}")
                segment_desc = segment.get("description", "")
                segment_size = segment.get("size", 0)
                segment_criteria = segment.get("criteria", {})
                segment_channel_dist = segment.get("channel_distribution", {})
                
                logger.debug(f"Segment data - Name: {segment_name}, Size: {segment_size}%, Channels: {segment_channel_dist}")
                
                db_segment = CustomerSegment(
                    name=segment_name,
                    description=segment_desc,
                    criteria=json.dumps(segment_criteria) if isinstance(segment_criteria, dict) else segment_criteria,
                    size=int(segment_size) if segment_size else 0,
                    channel_distribution=json.dumps(segment_channel_dist) if isinstance(segment_channel_dist, dict) else segment_channel_dist
                )
                session.add(db_segment)
                saved_segments.append(db_segment)
            
            session.commit()
            logger.info(f"Successfully saved {len(saved_segments)} segments to database")
            
            # Refresh to get IDs
            for segment in saved_segments:
                session.refresh(segment)
            
            response_data = {
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
            
            logger.info("=== Customer segment generation completed successfully ===")
            return response_data
            
        except Exception as e:
            logger.error(f"Error in generate_customer_segments: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error generating segments: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_customer_segments: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/segments", response_model=List[SegmentResponse])
async def get_customer_segments(session: Session = Depends(get_session)):
    """Get all customer segments"""
    logger.debug("Fetching all customer segments...")
    segments = session.exec(select(CustomerSegment)).all()
    logger.info(f"Retrieved {len(segments)} customer segments")
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
    from backend.services.campaign_service import execute_campaign
    background_tasks.add_task(execute_campaign, campaign_id)
    
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