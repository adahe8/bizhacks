# backend/agents/metrics_gather_agent.py
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any, Union
from datetime import datetime
from sqlmodel import Session, select
import logging
from uuid import UUID

from backend.core.config import settings
from data.database import engine
from data.models import Campaign, Metric, ContentAsset

logger = logging.getLogger(__name__)

def create_metrics_agent() -> Agent:
    """Create an agent for metrics gathering"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )
    
    agent = Agent(
        role="Marketing Analytics Specialist",
        goal="Collect and analyze campaign performance metrics across all channels",
        backstory="""You are an expert in marketing analytics who specializes in gathering
        and interpreting campaign performance data from various platforms.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    
    return agent

async def collect_all_metrics() -> List[Dict[str, Any]]:
    """Collect metrics for all active campaigns"""
    
    results = []
    
    with Session(engine) as session:
        # Get all active campaigns
        active_campaigns = session.exec(
            select(Campaign).where(Campaign.status == "active")
        ).all()
        
        for campaign in active_campaigns:
            try:
                # Collect metrics for this campaign
                metrics = await collect_campaign_metrics(
                    campaign_id=campaign.id,
                    channel=campaign.channel
                )
                
                # Store metrics in database
                for metric_data in metrics:
                    metric = Metric(
                        campaign_id=campaign.id,
                        platform=campaign.channel,
                        clicks=metric_data.get("clicks", 0),
                        impressions=metric_data.get("impressions", 0),
                        engagement_rate=metric_data.get("engagement_rate", 0.0),
                        conversion_rate=metric_data.get("conversion_rate", 0.0),
                        cpa=metric_data.get("cpa", 0.0),
                        timestamp=datetime.utcnow()
                    )
                    session.add(metric)
                
                results.append({
                    "campaign_id": ensure_str(campaign.id),
                    "campaign_name": campaign.name,
                    "metrics_collected": len(metrics)
                })
                
            except Exception as e:
                logger.error(f"Error collecting metrics for campaign {campaign.id}: {str(e)}")
                results.append({
                    "campaign_id": ensure_str(campaign.id),
                    "campaign_name": campaign.name,
                    "error": str(e)
                })
        
        session.commit()
    
    logger.info(f"Collected metrics for {len(results)} campaigns")
    return results

async def collect_campaign_metrics(campaign_id: Union[str, UUID], channel: str) -> List[Dict[str, Any]]:
    """Collect metrics for a specific campaign"""
    
    # Ensure campaign_id is UUID for database queries
    campaign_uuid = ensure_uuid(campaign_id)
    
    # Import the appropriate client based on channel
    if channel == "facebook":
        from external_apis.facebook_client import FacebookClient
        client = FacebookClient()
    elif channel == "email":
        from external_apis.email_client import EmailClient
        client = EmailClient()
    elif channel == "google_seo":
        from external_apis.google_ads_client import GoogleAdsClient
        client = GoogleAdsClient()
    else:
        raise ValueError(f"Unsupported channel: {channel}")
    
    # Get published content assets for this campaign
    with Session(engine) as session:
        assets = session.exec(
            select(ContentAsset)
            .where(ContentAsset.campaign_id == campaign_uuid)
            .where(ContentAsset.status == "published")
        ).all()
        
        if not assets:
            logger.warning(f"No published assets found for campaign {campaign_uuid}")
            return []
        
        # Collect metrics for each asset
        all_metrics = []
        for asset in assets:
            try:
                # Get metrics from the platform
                asset_metrics = await client.get_metrics(
                    asset_id=ensure_str(asset.id),
                    published_at=asset.published_at
                )
                all_metrics.append(asset_metrics)
            except Exception as e:
                logger.error(f"Error collecting metrics for asset {asset.id}: {str(e)}")
        
        return all_metrics
