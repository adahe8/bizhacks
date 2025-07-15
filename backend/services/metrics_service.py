# backend/services/metrics_service.py
from sqlmodel import Session, select
from datetime import datetime, timedelta
import logging
import random
from typing import List, Dict, Any

from data.database import get_db_session
from data.models import Campaign, CampaignMetrics, ChannelType
from backend.external_apis.facebook_client import FacebookClient
from backend.external_apis.email_client import EmailClient
from backend.external_apis.google_ads_client import GoogleAdsClient

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for gathering and processing campaign metrics"""
    
    @staticmethod
    async def gather_all_metrics():
        """Gather metrics for all running campaigns"""
        with get_db_session() as session:
            # Get all running campaigns
            campaigns = session.exec(
                select(Campaign).where(Campaign.status == "running")
            ).all()
            
            for campaign in campaigns:
                try:
                    await MetricsService.gather_campaign_metrics(campaign.id)
                except Exception as e:
                    logger.error(f"Error gathering metrics for campaign {campaign.id}: {str(e)}")
    
    @staticmethod
    async def gather_campaign_metrics(campaign_id: int):
        """Gather metrics for a specific campaign"""
        with get_db_session() as session:
            campaign = session.get(Campaign, campaign_id)
            if not campaign:
                return
            
            # Get appropriate client based on channel
            if campaign.channel == ChannelType.FACEBOOK:
                client = FacebookClient()
                # Simulate getting metrics from Facebook
                raw_metrics = await client.get_ad_metrics(f"campaign_{campaign_id}")
            elif campaign.channel == ChannelType.EMAIL:
                client = EmailClient()
                raw_metrics = await client.get_campaign_metrics(f"campaign_{campaign_id}")
            elif campaign.channel == ChannelType.GOOGLE_ADS:
                client = GoogleAdsClient()
                raw_metrics = await client.get_ad_performance(f"campaign_{campaign_id}")
            else:
                return
            
            # Process and save metrics
            metrics = CampaignMetrics(
                campaign_id=campaign_id,
                channel=campaign.channel,
                metric_date=datetime.utcnow(),
                impressions=raw_metrics.get('impressions', 0),
                clicks=raw_metrics.get('clicks', 0),
                conversions=raw_metrics.get('conversions', 0),
                spend=raw_metrics.get('spend', 0),
                engagement_rate=MetricsService._calculate_engagement_rate(raw_metrics),
                ctr=raw_metrics.get('ctr', 0),
                cpc=raw_metrics.get('cpc', 0) if campaign.channel == ChannelType.GOOGLE_ADS else raw_metrics.get('clicks', 0) / raw_metrics.get('spend', 1) if raw_metrics.get('spend', 0) > 0 else 0,
                roi=MetricsService._calculate_roi(raw_metrics),
                custom_metrics=str(raw_metrics)
            )
            
            session.add(metrics)
            session.commit()
            
            logger.info(f"Gathered metrics for campaign {campaign_id}")
    
    @staticmethod
    def _calculate_engagement_rate(metrics: Dict[str, Any]) -> float:
        """Calculate engagement rate based on channel-specific metrics"""
        if 'engagement' in metrics:
            # Facebook style
            total_engagement = sum(metrics['engagement'].values())
            impressions = metrics.get('impressions', 1)
            return (total_engagement / impressions) * 100 if impressions > 0 else 0
        elif 'open_rate' in metrics:
            # Email style
            return metrics.get('open_rate', 0)
        else:
            # Default to CTR
            return metrics.get('ctr', 0)
    
    @staticmethod
    def _calculate_roi(metrics: Dict[str, Any]) -> float:
        """Calculate ROI from metrics"""
        spend = metrics.get('spend', 0)
        conversions = metrics.get('conversions', 0)
        avg_order_value = 50  # Mock average order value
        
        if spend > 0:
            revenue = conversions * avg_order_value
            return (revenue - spend) / spend
        return 0.0