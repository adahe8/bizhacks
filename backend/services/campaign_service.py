# backend/services/campaign_service.py
from sqlmodel import Session
from typing import Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import logging

from data.models import Campaign, Schedule
from backend.core.scheduler import schedule_campaign_execution, schedule_recurring_campaign, cancel_job
from backend.agents.orchestrator_agent import rebalance_budgets

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, session: Session):
        self.session = session
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Campaign:
        """Create a new campaign and schedule it"""
        campaign = Campaign(**campaign_data)
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        
        # Automatically create schedules based on frequency and start_date
        if campaign.frequency and campaign.start_date:
            await self._create_campaign_schedules(campaign, months=6)
            logger.info(f"Created campaign {campaign.name} with 6 months of schedules")
        
        # Trigger budget rebalancing for all active campaigns
        await rebalance_budgets()
        
        return campaign
    
    async def activate_campaign(self, campaign_id: UUID) -> Campaign:
        """Activate a campaign and create schedules if not already created"""
        campaign = self.session.get(Campaign, campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Update status
        campaign.status = "active"
        campaign.updated_at = datetime.utcnow()
        
        # Check if schedules already exist
        existing_schedules = self.session.query(Schedule).filter(
            Schedule.campaign_id == campaign.id
        ).count()
        
        # Create schedules if none exist
        if existing_schedules == 0 and campaign.frequency and campaign.start_date:
            await self._create_campaign_schedules(campaign, months=6)
        
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        
        logger.info(f"Activated campaign {campaign.name} with frequency {campaign.frequency}")
        
        return campaign
    
    async def _create_campaign_schedules(self, campaign: Campaign, months: int = 6):
        """Create schedule entries based on campaign frequency for specified months"""
        if not campaign.frequency or not campaign.start_date:
            return
        
        # Clear existing pending schedules
        existing_schedules = self.session.query(Schedule).filter(
            Schedule.campaign_id == campaign.id,
            Schedule.status == "pending"
        ).all()
        
        for schedule in existing_schedules:
            if schedule.job_id:
                cancel_job(schedule.job_id)
            self.session.delete(schedule)
        
        # Create new schedules for the specified period (default 6 months)
        current_date = campaign.start_date
        end_date = current_date + timedelta(days=30 * months)  # Approximate months
        
        schedule_count = 0
        while current_date <= end_date:
            # Create schedule entry
            job_id = f"{campaign.id}_{current_date.isoformat()}"
            schedule = Schedule(
                campaign_id=campaign.id,
                scheduled_time=current_date,
                status="pending",
                job_id=job_id
            )
            self.session.add(schedule)
            
            # Schedule with APScheduler
            schedule_campaign_execution(str(campaign.id), current_date, job_id)
            schedule_count += 1
            
            # Calculate next date based on frequency
            if campaign.frequency == "daily":
                current_date += timedelta(days=1)
            elif campaign.frequency == "weekly":
                current_date += timedelta(weeks=1)
            elif campaign.frequency == "monthly":
                # More accurate monthly calculation
                # Add one month properly (handle month boundaries)
                if current_date.month == 12:
                    next_month = 1
                    next_year = current_date.year + 1
                else:
                    next_month = current_date.month + 1
                    next_year = current_date.year
                
                try:
                    current_date = current_date.replace(month=next_month, year=next_year)
                except ValueError:
                    # Handle cases like Jan 31 -> Feb 31 (doesn't exist)
                    # Move to last day of next month
                    import calendar
                    last_day = calendar.monthrange(next_year, next_month)[1]
                    current_date = current_date.replace(month=next_month, year=next_year, day=last_day)
            else:
                break
        
        self.session.commit()
        logger.info(f"Created {schedule_count} schedules for campaign {campaign.name} over {months} months")

async def execute_campaign(campaign_id: str):
    """Execute a campaign (called by scheduler)"""
    from sqlmodel import Session
    from data.database import engine
    from backend.agents.campaign_execution_agent import execute_campaign_content
    
    with Session(engine) as session:
        campaign = session.get(Campaign, UUID(campaign_id))
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return
        
        # Find the schedule being executed
        schedule = session.query(Schedule).filter(
            Schedule.campaign_id == campaign.id,
            Schedule.status == "pending"
        ).order_by(Schedule.scheduled_time).first()
        
        if schedule:
            schedule.status = "executing"
            session.add(schedule)
            session.commit()
        
        try:
            # Execute the campaign
            logger.info(f"Executing campaign {campaign.name}")
            await execute_campaign_content(campaign_id)
            
            if schedule:
                schedule.status = "completed"
                schedule.executed_at = datetime.utcnow()
                session.add(schedule)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error executing campaign {campaign_id}: {str(e)}")
            if schedule:
                schedule.status = "failed"
                session.add(schedule)
                session.commit()