from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any
import logging

from data.database import engine
from data.models import Campaign, Schedule, SetupConfiguration
from agents.crew_factory import create_campaign_crew
from core.scheduler import schedule_recurring_campaign
from services.crew_service import CrewService

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, session: Session):
        self.session = session
        self.crew_service = CrewService()
    
    async def activate_campaign(self, campaign_id: UUID) -> Campaign:
        """Activate a campaign and schedule it"""
        campaign = self.session.get(Campaign, campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign.status == "active":
            return campaign
        
        # Update status
        campaign.status = "active"
        campaign.updated_at = datetime.utcnow()
        
        # Schedule recurring execution based on frequency
        if campaign.frequency:
            job_id = f"campaign_{campaign_id}_recurring"
            schedule_recurring_campaign(
                str(campaign_id),
                campaign.frequency,
                job_id
            )
            
            # Create schedule record
            schedule = Schedule(
                campaign_id=campaign_id,
                scheduled_time=datetime.utcnow(),
                status="pending",
                job_id=job_id
            )
            self.session.add(schedule)
        
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        
        logger.info(f"Activated campaign {campaign.name} (ID: {campaign_id})")
        return campaign
    
    async def execute_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Execute a campaign using CrewAI agents"""
        with Session(engine) as session:
            campaign = session.get(Campaign, UUID(campaign_id))
            if not campaign:
                raise ValueError("Campaign not found")
            
            if campaign.status != "active":
                logger.warning(f"Campaign {campaign_id} is not active, skipping execution")
                return {"status": "skipped", "reason": "Campaign not active"}
            
            # Get setup configuration for context
            setup = session.exec(
                select(SetupConfiguration).where(SetupConfiguration.is_active == True)
            ).first()
            
            if not setup:
                raise ValueError("No active setup configuration found")
            
            logger.info(f"Executing campaign {campaign.name} on channel {campaign.channel}")
            
            try:
                # Create campaign crew
                crew = create_campaign_crew(
                    campaign_id=campaign_id,
                    channel=campaign.channel,
                    product_info={
                        "id": str(campaign.product_id),
                        "name": campaign.product.product_name if campaign.product else "",
                        "description": campaign.product.description if campaign.product else ""
                    },
                    market_details=setup.market_details,
                    strategic_goals=setup.strategic_goals,
                    guardrails=setup.guardrails
                )
                
                # Execute crew
                result = await self.crew_service.execute_crew(crew, {
                    "campaign_name": campaign.name,
                    "campaign_description": campaign.description,
                    "customer_segment": campaign.customer_segment,
                    "budget": campaign.budget
                })
                
                # Update execution record
                schedules = session.exec(
                    select(Schedule)
                    .where(Schedule.campaign_id == UUID(campaign_id))
                    .where(Schedule.status == "pending")
                ).all()
                
                for schedule in schedules:
                    schedule.status = "completed"
                    schedule.executed_at = datetime.utcnow()
                    session.add(schedule)
                
                session.commit()
                
                logger.info(f"Campaign {campaign.name} executed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error executing campaign {campaign_id}: {str(e)}")
                
                # Update schedule status to failed
                schedules = session.exec(
                    select(Schedule)
                    .where(Schedule.campaign_id == UUID(campaign_id))
                    .where(Schedule.status == "pending")
                ).all()
                
                for schedule in schedules:
                    schedule.status = "failed"
                    session.add(schedule)
                
                session.commit()
                raise

# Global function for scheduler
async def execute_campaign(campaign_id: str):
    """Global function to execute a campaign (called by scheduler)"""
    service = CampaignService(Session(engine))
    return await service.execute_campaign(campaign_id)