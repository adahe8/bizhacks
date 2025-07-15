# backend/services/campaign_service.py
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any, Union
import logging

from data.database import engine
from data.models import Campaign, Schedule, SetupConfiguration
from agents.crew_factory import create_campaign_crew
from core.scheduler import schedule_recurring_campaign
from backend.services.crew_service import CrewService
from backend.services.metrics_generator_service import MetricsGeneratorService

logger = logging.getLogger(__name__)

def ensure_uuid(value: Union[str, UUID]) -> UUID:
    """Convert string to UUID if needed"""
    if isinstance(value, str):
        return UUID(value)
    return value

def ensure_str(value: Union[str, UUID]) -> str:
    """Convert UUID to string if needed"""
    if isinstance(value, UUID):
        return str(value)
    return value

class CampaignService:
    def __init__(self, session: Session):
        self.session = session
        self.crew_service = CrewService()
        self.metrics_service = MetricsGeneratorService()
    
    async def activate_campaign(self, campaign_id: Union[str, UUID]) -> Campaign:
        """Activate a campaign and schedule it"""
        campaign_uuid = ensure_uuid(campaign_id)
        
        campaign = self.session.get(Campaign, campaign_uuid)
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign.status == "active":
            return campaign
        
        # Update status
        campaign.status = "active"
        campaign.updated_at = datetime.utcnow()
        
        # Schedule recurring execution based on frequency
        if campaign.frequency:
            job_id = f"campaign_{ensure_str(campaign_uuid)}_recurring"
            schedule_recurring_campaign(
                ensure_str(campaign_uuid),  # Scheduler needs string
                campaign.frequency,
                job_id
            )
            
            # Create schedule record
            schedule = Schedule(
                campaign_id=campaign_uuid,  # Database needs UUID
                scheduled_time=datetime.utcnow(),
                status="pending",
                job_id=job_id
            )
            self.session.add(schedule)
        
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        
        logger.info(f"Activated campaign {campaign.name} (ID: {campaign_uuid})")
        return campaign
    
    async def execute_campaign(self, campaign_id: Union[str, UUID]) -> Dict[str, Any]:
        """Execute a campaign using CrewAI agents"""
        campaign_uuid = ensure_uuid(campaign_id)
        
        with Session(engine) as session:
            campaign = session.get(Campaign, campaign_uuid)
            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_uuid}")
            
            if campaign.status != "active":
                logger.warning(f"Campaign {campaign_uuid} is not active, skipping execution")
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
                    campaign_id=campaign_uuid,  # Pass UUID object
                    channel=campaign.channel,
                    product_info={
                        "id": ensure_str(campaign.product_id),
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
                
                # Generate metrics for this execution
                metric = await self.metrics_service.generate_and_store_metrics(campaign_uuid)
                
                # Update execution record
                schedules = session.exec(
                    select(Schedule)
                    .where(Schedule.campaign_id == campaign_uuid)
                    .where(Schedule.status == "pending")
                ).all()
                
                for schedule in schedules:
                    schedule.status = "completed"
                    schedule.executed_at = datetime.utcnow()
                    session.add(schedule)
                
                session.commit()
                
                logger.info(f"Campaign {campaign.name} executed successfully with reach impact")
                return {
                    **result,
                    "metrics_generated": True,
                    "metric_id": ensure_str(metric.id)
                }
                
            except Exception as e:
                logger.error(f"Error executing campaign {campaign_uuid}: {str(e)}")
                
                # Update schedule status to failed
                schedules = session.exec(
                    select(Schedule)
                    .where(Schedule.campaign_id == campaign_uuid)
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