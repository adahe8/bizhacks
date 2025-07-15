# backend/api/schedules.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta

from data.database import get_session
from data.models import Campaign, CampaignStatus
from backend.core.scheduler import scheduler, schedule_campaign
from pydantic import BaseModel

router = APIRouter()

class ScheduleUpdate(BaseModel):
    frequency_days: int
    start_date: Optional[datetime] = None

@router.get("/")
async def get_schedules(session: Session = Depends(get_session)):
    """Get all scheduled campaigns"""
    campaigns = session.exec(
        select(Campaign).where(Campaign.status == CampaignStatus.RUNNING)
    ).all()
    
    schedules = []
    for campaign in campaigns:
        job = scheduler.get_job(f"campaign_{campaign.id}")
        if job:
            schedules.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "next_run": job.next_run_time,
                "frequency_days": campaign.frequency_days
            })
    
    return schedules

@router.post("/{campaign_id}/schedule")
async def schedule_campaign_execution(
    campaign_id: int,
    schedule_data: ScheduleUpdate,
    session: Session = Depends(get_session)
):
    """Schedule a campaign for execution"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Campaign must be approved first")
    
    # Update campaign
    campaign.frequency_days = schedule_data.frequency_days
    campaign.status = CampaignStatus.RUNNING
    campaign.next_execution = schedule_data.start_date or datetime.utcnow()
    
    session.add(campaign)
    session.commit()
    
    # Schedule with APScheduler
    schedule_campaign(campaign_id, campaign.frequency_days)
    
    return {"message": "Campaign scheduled", "next_execution": campaign.next_execution}

@router.delete("/{campaign_id}/schedule")
async def unschedule_campaign(
    campaign_id: int,
    session: Session = Depends(get_session)
):
    """Stop a scheduled campaign"""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Remove from scheduler
    job_id = f"campaign_{campaign_id}"
    scheduler.remove_job(job_id)
    
    # Update campaign status
    campaign.status = CampaignStatus.PAUSED
    session.add(campaign)
    session.commit()
    
    return {"message": "Campaign unscheduled"}