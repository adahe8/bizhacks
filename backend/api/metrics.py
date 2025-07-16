# backend/api/metrics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel

from data.database import get_session
from data.models import Metric, Campaign

router = APIRouter()

class MetricResponse(BaseModel):
    id: UUID
    campaign_id: Optional[UUID]
    platform: Optional[str]
    clicks: int
    impressions: int
    engagement_rate: float
    conversion_rate: float
    cpa: float
    timestamp: datetime

class MetricsSummary(BaseModel):
    campaign_id: UUID
    campaign_name: str
    channel: str
    total_clicks: int
    total_impressions: int
    avg_engagement_rate: float
    avg_conversion_rate: float
    avg_cpa: float
    total_spend: float
    roi: float

class ChannelMetrics(BaseModel):
    channel: str
    total_campaigns: int
    total_clicks: int
    total_impressions: int
    avg_engagement_rate: float
    avg_conversion_rate: float
    total_spend: float

@router.get("/campaign/{campaign_id}", response_model=List[MetricResponse])
async def get_campaign_metrics(
    campaign_id: UUID,
    session: Session = Depends(get_session),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get metrics for a specific campaign"""
    # Verify campaign exists
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Build query
    query = select(Metric).where(Metric.campaign_id == campaign_id)
    
    if start_date:
        query = query.where(Metric.timestamp >= start_date)
    if end_date:
        query = query.where(Metric.timestamp <= end_date)
    
    metrics = session.exec(query.order_by(Metric.timestamp.desc())).all()
    
    return metrics

@router.get("/summary", response_model=List[MetricsSummary])
async def get_metrics_summary(
    session: Session = Depends(get_session),
    days: int = Query(7, description="Number of days to look back")
):
    """Get metrics summary for all campaigns"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all campaigns with their metrics
    campaigns = session.exec(select(Campaign)).all()
    
    summaries = []
    for campaign in campaigns:
        # Get metrics for this campaign
        metrics = session.exec(
            select(Metric)
            .where(Metric.campaign_id == campaign.id)
            .where(Metric.timestamp >= start_date)
        ).all()
        
        if metrics:
            total_clicks = sum(m.clicks or 0 for m in metrics)
            total_impressions = sum(m.impressions or 0 for m in metrics)
            avg_engagement_rate = sum(m.engagement_rate or 0 for m in metrics) / len(metrics)
            avg_conversion_rate = sum(m.conversion_rate or 0 for m in metrics) / len(metrics)
            avg_cpa = sum(m.cpa or 0 for m in metrics) / len(metrics)
            total_spend = campaign.budget * (days / 30)  # Approximate monthly budget to period
            roi = (avg_conversion_rate * 100) - 100 if avg_conversion_rate > 0 else -100
            
            summaries.append(MetricsSummary(
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                channel=campaign.channel,
                total_clicks=total_clicks,
                total_impressions=total_impressions,
                avg_engagement_rate=avg_engagement_rate,
                avg_conversion_rate=avg_conversion_rate,
                avg_cpa=avg_cpa,
                total_spend=total_spend,
                roi=roi
            ))
    
    return summaries

@router.get("/channels", response_model=List[ChannelMetrics])
async def get_channel_metrics(
    session: Session = Depends(get_session),
    days: int = Query(7, description="Number of days to look back")
):
    """Get aggregated metrics by channel"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    channels = ["facebook", "email", "google_seo"]
    channel_metrics = []
    
    for channel in channels:
        # Get campaigns for this channel
        campaigns = session.exec(
            select(Campaign).where(Campaign.channel == channel)
        ).all()
        
        if campaigns:
            total_clicks = 0
            total_impressions = 0
            total_engagement = 0
            total_conversion = 0
            metric_count = 0
            total_spend = sum(c.budget * (days / 30) for c in campaigns)
            
            for campaign in campaigns:
                metrics = session.exec(
                    select(Metric)
                    .where(Metric.campaign_id == campaign.id)
                    .where(Metric.timestamp >= start_date)
                ).all()
                
                for metric in metrics:
                    total_clicks += metric.clicks or 0
                    total_impressions += metric.impressions or 0
                    total_engagement += metric.engagement_rate or 0
                    total_conversion += metric.conversion_rate or 0
                    metric_count += 1
            
            channel_metrics.append(ChannelMetrics(
                channel=channel,
                total_campaigns=len(campaigns),
                total_clicks=total_clicks,
                total_impressions=total_impressions,
                avg_engagement_rate=total_engagement / metric_count if metric_count > 0 else 0,
                avg_conversion_rate=total_conversion / metric_count if metric_count > 0 else 0,
                total_spend=total_spend
            ))
        else:
            channel_metrics.append(ChannelMetrics(
                channel=channel,
                total_campaigns=0,
                total_clicks=0,
                total_impressions=0,
                avg_engagement_rate=0,
                avg_conversion_rate=0,
                total_spend=0
            ))
    
    return channel_metrics

@router.post("/collect")
async def trigger_metrics_collection(
    session: Session = Depends(get_session)
):
    """Manually trigger metrics collection for all active campaigns"""
    from agents.metrics_gather_agent import collect_all_metrics
    
    try:
        results = await collect_all_metrics()
        return {
            "message": "Metrics collection completed",
            "campaigns_updated": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting metrics: {str(e)}")