from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from data.database import get_session
from data.models import Schedule, Campaign
from core.scheduler import schedule_campaign_execution, schedule_recurring_campaign, cancel_job
import uuid

router = APIRouter()

class ScheduleCreate(BaseModel):
    campaign_id: UUID
    scheduled_time: datetime
    recurring: bool = False

class ScheduleResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    scheduled_time: datetime
    status: str
    job_id: Optional[str]
    created_at: datetime
    executed_at: Optional[datetime]

class ScheduleUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None

@router.get("/", response_model=List[ScheduleResponse])
async def list_schedules(
    session: Session = Depends(get_session),
    campaign_id: Optional[UUID] = None,
    status: Optional[str] = None
):
    """List all schedules with optional filters"""
    query = select(Schedule)
    
    if campaign_id:
        query = query.where(Schedule.campaign_id == campaign_id)
    if status:
        query = query.where(Schedule.status == status)
    
    schedules = session.exec(query.order_by(Schedule.scheduled_time)).all()
    
    return schedules

@router.post("/", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    session: Session = Depends(get_session)
):
    """Create a new schedule for a campaign"""
    # Verify campaign exists and is active
    campaign = session.get(Campaign, schedule_data.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign must be active to schedule")
    
    # Create schedule record
    job_id = str(uuid.uuid4())
    schedule = Schedule(
        campaign_id=schedule_data.campaign_id,
        scheduled_time=schedule_data.scheduled_time,
        status="pending",
        job_id=job_id
    )
    
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    
    # Schedule with APScheduler
    if schedule_data.recurring and campaign.frequency:
        schedule_recurring_campaign(
            str(campaign.id),
            campaign.frequency,
            job_id
        )
    else:
        schedule_campaign_execution(
            str(campaign.id),
            schedule_data.scheduled_time,
            job_id
        )
    
    return schedule

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    session: Session = Depends(get_session)
):
    """Get a specific schedule"""
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    schedule_update: ScheduleUpdate,
    session: Session = Depends(get_session)
):
    """Update a schedule"""
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Update fields
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    # If time was updated and schedule is pending, reschedule
    if schedule_update.scheduled_time and schedule.status == "pending" and schedule.job_id:
        cancel_job(schedule.job_id)
        schedule_campaign_execution(
            str(schedule.campaign_id),
            schedule_update.scheduled_time,
            schedule.job_id
        )
    
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    
    return schedule

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: UUID,
    session: Session = Depends(get_session)
):
    """Cancel and delete a schedule"""
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Cancel job if pending
    if schedule.status == "pending" and schedule.job_id:
        cancel_job(schedule.job_id)
    
    session.delete(schedule)
    session.commit()
    
    return {"message": "Schedule deleted successfully"}

@router.get("/upcoming", response_model=List[ScheduleResponse])
async def get_upcoming_schedules(
    session: Session = Depends(get_session),
    days: int = 7
):
    """Get upcoming schedules for the next N days"""
    from datetime import timedelta
    
    now = datetime.utcnow()
    end_date = now + timedelta(days=days)
    
    schedules = session.exec(
        select(Schedule)
        .where(Schedule.scheduled_time >= now)
        .where(Schedule.scheduled_time <= end_date)
        .where(Schedule.status == "pending")
        .order_by(Schedule.scheduled_time)
    ).all()
    
    return schedules