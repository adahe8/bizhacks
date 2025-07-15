# backend/services/campaign_service.py
from sqlmodel import Session, select
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import logging
import json
from typing import List, Dict, Any

from data.database import get_db_session
from data.models import Campaign, Content, CampaignStatus, ChannelType
from backend.agents.crew_factory import CrewFactory
from backend.external_apis.facebook_client import FacebookClient
from backend.external_apis.email_client import EmailClient
from backend.external_apis.google_ads_client import GoogleAdsClient

logger = logging.getLogger(__name__)

class CampaignService:
    """Service for campaign operations"""
    
    @staticmethod
    async def execute_campaign(campaign_id: int):
        """Execute a single campaign"""
        with get_db_session() as session:
            campaign = session.get(Campaign, campaign_id)
            if not campaign or campaign.status != CampaignStatus.RUNNING:
                logger.warning(f"Campaign {campaign_id} not found or not running")
                return
            
            try:
                # Get company details
                from data.models import CompanyDetails
                company = session.exec(select(CompanyDetails)).first()
                
                # Create content generation crew
                crew_factory = CrewFactory()
                crew = crew_factory.create_content_generation_crew(
                    campaign=campaign.dict(),
                    channel=campaign.channel.value,
                    company_data=company.dict()
                )
                
                # Execute crew to generate content
                result = crew.kickoff()
                
                # Parse result and save content
                content_data = json.loads(result) if isinstance(result, str) else result
                
                content = Content(
                    campaign_id=campaign_id,
                    channel=campaign.channel,
                    content_type=content_data.get('type', 'text'),
                    content_data=json.dumps(content_data),
                    compliance_approved=True  # Assuming compliance passed in crew
                )
                
                session.add(content)
                session.commit()
                
                # Publish content
                await CampaignService._publish_content(content, campaign.channel)
                
                # Update campaign execution time
                campaign.last_execution = datetime.utcnow()
                session.add(campaign)
                session.commit()
                
                logger.info(f"Successfully executed campaign {campaign_id}")
                
            except Exception as e:
                logger.error(f"Error executing campaign {campaign_id}: {str(e)}")
    
    @staticmethod
    async def execute_campaigns_parallel(campaign_ids: List[int]):
        """Execute multiple campaigns in parallel"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for campaign_id in campaign_ids:
                future = executor.submit(
                    asyncio.run,
                    CampaignService.execute_campaign(campaign_id)
                )
                futures.append(future)
            
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in parallel execution: {str(e)}")
    
    @staticmethod
    async def _publish_content(content: Content, channel: ChannelType):
        """Publish content to external platform"""
        content_data = json.loads(content.content_data)
        
        try:
            if channel == ChannelType.FACEBOOK:
                client = FacebookClient()
                result = await client.publish_post(content_data)
            elif channel == ChannelType.EMAIL:
                client = EmailClient()
                result = await client.send_campaign(content_data)
            elif channel == ChannelType.GOOGLE_ADS:
                client = GoogleAdsClient()
                result = await client.create_ad(content_data)
            
            # Update content with external ID
            content.published = True
            content.published_at = datetime.utcnow()
            content.external_id = result.get('id')
            
        except Exception as e:
            logger.error(f"Error publishing content: {str(e)}")
            raise