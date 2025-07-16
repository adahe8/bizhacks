# backend/api/agents.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
import logging
import traceback

from data.database import get_session
from data.models import CustomerSegment, Campaign, SetupConfiguration
from backend.services.campaign_service import CampaignService
from backend.agents.segmentation_agent import generate_customer_segments
from backend.agents.campaign_creation_agent import generate_campaign_ideas
from backend.agents.orchestrator_agent import rebalance_budgets
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
    size: Optional[float]  # ✅ FIXED: Changed from int to float
    
    class Config:
        # Ensure UUIDs are serialized as strings in JSON
        json_encoders = {
            UUID: lambda v: str(v)
        }

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

from sqlmodel import Session, select, delete

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
        
        # Delete ALL existing segments to prevent duplicates
        logger.debug("Deleting ALL existing customer segments...")
        session.exec(delete(CustomerSegment))  # Use delete statement
        session.commit()
        logger.info("Cleared all existing segments")
        
        # Generate segments
        logger.info("Calling generate_customer_segments...")
        try:
            segments = await generate_customer_segments(
                product_id=str(setup.product_id),
                market_details=json.loads(setup.market_details) if setup.market_details else {},
                strategic_goals=setup.strategic_goals or ""
            )
            
            logger.info(f"Generated {len(segments)} segments from segmentation agent")
            
            # Verify we have exactly 3 segments (or less)
            if len(segments) > 3:
                logger.warning(f"Generated {len(segments)} segments, limiting to 3")
                segments = segments[:3]
            
            # The segments are already saved by generate_customer_segments
            # Just need to fetch them for response
            saved_segments = session.exec(select(CustomerSegment)).all()
            
            # Double-check we don't have duplicates
            if len(saved_segments) != len(segments):
                logger.warning(f"Mismatch: generated {len(segments)} but saved {len(saved_segments)}")
            
            response_data = {
                "message": f"Generated {len(saved_segments)} unique customer segments successfully",
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
            
        except ValueError as e:
            # Handle specific value errors (e.g., invalid product ID)
            logger.error(f"ValueError in generate_customer_segments: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
            
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Market details: {setup.market_details}")
            raise HTTPException(status_code=500, detail="Error parsing configuration data")
            
        except Exception as e:
            # Handle any other errors from generate_customer_segments
            logger.error(f"Error in generate_customer_segments: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Check if it's a Gemini API key error
            if "GEMINI_API_KEY" in str(e):
                raise HTTPException(
                    status_code=503, 
                    detail="AI service not configured. Please check your GEMINI_API_KEY configuration."
                )
            
            raise HTTPException(status_code=500, detail=f"Error generating segments: {str(e)}")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error in create_customer_segments: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Rollback any database changes
        session.rollback()
        
        # Provide user-friendly error message
        if "database" in str(e).lower():
            raise HTTPException(status_code=500, detail="Database error. Please try again.")
        elif "connection" in str(e).lower():
            raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")
        else:
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
    
@router.post("/generate-campaigns")
async def generate_campaigns(session: Session = Depends(get_session)):
    """Generate campaign ideas using AI agents and create them with schedules"""
    # Get current setup configuration
    setup = session.query(SetupConfiguration).filter(
        SetupConfiguration.is_active == True
    ).first()
    
    if not setup:
        raise HTTPException(status_code=400, detail="No active setup configuration found")
    
    if not setup.product_id:
        raise HTTPException(status_code=400, detail="No product selected in setup")
    
    try:
        # Generate segments if not already done
        from backend.agents.segmentation_agent import generate_customer_segments
        from data.models import CustomerSegment
        
        existing_segments = session.query(CustomerSegment).count()
        if existing_segments == 0:
            logger.info("No segments found, generating...")
            segments_data = await generate_customer_segments()
            # Save segments (implementation details...)
        
        # Get segments for campaign generation
        segments = session.query(CustomerSegment).all()
        segment_names = [s.name for s in segments]
        
        # Generate campaign ideas
        from backend.agents.campaign_creation_agent import generate_campaign_ideas
        
        channels = ["facebook", "email", "google_seo"]
        campaign_ideas = await generate_campaign_ideas(
            segments=segment_names,
            channels=channels,
            strategic_goals=setup.strategic_goals or "Increase brand awareness and sales",
            monthly_budget=setup.monthly_budget,
            campaign_count=setup.campaign_count
        )
        
        # Create campaigns with scheduling using CampaignService
        created_campaigns = []
        service = CampaignService(session)
        
        for idea in campaign_ideas:
            # Ensure start_date is properly formatted
            if 'start_date' in idea and idea['start_date']:
                if isinstance(idea['start_date'], str):
                    idea['start_date'] = datetime.fromisoformat(idea['start_date'].replace('Z', '+00:00'))
            else:
                idea['start_date'] = datetime.utcnow()
            
            campaign_data = {
                "product_id": setup.product_id,
                "name": idea["name"],
                "description": idea["description"],
                "channel": idea["channel"],
                "customer_segment": idea["customer_segment"],
                "frequency": idea["frequency"],
                "start_date": idea["start_date"],
                "budget": idea["suggested_budget"],
                "status": "active"  # Set active to enable scheduling
            }
            
            # Create campaign with automatic scheduling
            campaign = await service.create_campaign(campaign_data)
            created_campaigns.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "channel": campaign.channel,
                "customer_segment": campaign.customer_segment,
                "frequency": campaign.frequency,
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "budget": campaign.budget,
                "status": campaign.status,
                "messaging": idea.get("messaging", []),
                "objectives": idea.get("objectives", {}),
                "expected_outcomes": idea.get("expected_outcomes", "")
            })
            
            logger.info(f"Created campaign '{campaign.name}' with 6 months of schedules")
        
        return {
            "message": f"Successfully generated and scheduled {len(created_campaigns)} campaigns",
            "campaigns": created_campaigns
        }
        
    except Exception as e:
        logger.error(f"Error generating campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating campaigns: {str(e)}")