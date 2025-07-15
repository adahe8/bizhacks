# backend/api/agents.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Dict, Any
import json

from data.database import get_session
from data.models import CompanyDetails, Customer, CustomerSegment, Campaign
from backend.agents.crew_factory import CrewFactory
from backend.services.agent_service import AgentService
from pydantic import BaseModel

router = APIRouter()

class SegmentationRequest(BaseModel):
    use_uploaded_data: bool = True

class CampaignGenerationRequest(BaseModel):
    segment_ids: List[int]
    campaigns_per_segment: int = 3

class BudgetRebalanceRequest(BaseModel):
    force: bool = False

@router.post("/segment-customers")
async def run_segmentation(
    request: SegmentationRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Run customer segmentation agent"""
    company = session.exec(select(CompanyDetails)).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not setup")
    
    # Get customer data
    customers = session.exec(select(Customer)).all()
    if not customers:
        raise HTTPException(status_code=400, detail="No customer data available")
    
    # Run segmentation in background
    background_tasks.add_task(
        AgentService.run_segmentation,
        company_id=company.id,
        customer_data=[c.dict() for c in customers]
    )
    
    return {"message": "Segmentation started", "status": "processing"}

@router.post("/generate-campaigns")
async def generate_campaigns(
    request: CampaignGenerationRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Generate campaign ideas using AI"""
    company = session.exec(select(CompanyDetails)).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not setup")
    
    # Validate segments exist
    segments = []
    for seg_id in request.segment_ids:
        segment = session.get(CustomerSegment, seg_id)
        if not segment:
            raise HTTPException(status_code=404, detail=f"Segment {seg_id} not found")
        segments.append(segment)
    
    # Run campaign generation in background
    background_tasks.add_task(
        AgentService.generate_campaigns,
        company_id=company.id,
        segment_ids=request.segment_ids
    )
    
    return {"message": "Campaign generation started", "segments": len(segments)}

@router.post("/rebalance-budgets")
async def rebalance_budgets(
    request: BudgetRebalanceRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Run budget rebalancing across campaigns"""
    campaigns = session.exec(
        select(Campaign).where(Campaign.status == CampaignStatus.RUNNING)
    ).all()
    
    if not campaigns:
        raise HTTPException(status_code=400, detail="No running campaigns")
    
    # Run rebalancing in background
    background_tasks.add_task(
        AgentService.rebalance_budgets,
        campaign_ids=[c.id for c in campaigns]
    )
    
    return {"message": "Budget rebalancing started", "campaigns": len(campaigns)}

@router.get("/status/{task_type}/{task_id}")
async def get_agent_task_status(task_type: str, task_id: str):
    """Get status of an agent task"""
    # In a real implementation, this would check task status
    # For now, return a mock status
    return {
        "task_type": task_type,
        "task_id": task_id,
        "status": "completed",
        "result": "Task completed successfully"
    }