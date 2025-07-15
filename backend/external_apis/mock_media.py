from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import uuid

router = APIRouter()

# Mock data storage
mock_campaigns = {}
mock_metrics = {}

class MockFacebookPost(BaseModel):
    message: str
    link: Optional[str] = None
    targeting: Optional[Dict[str, Any]] = None
    scheduled_publish_time: Optional[str] = None

class MockEmailCampaign(BaseModel):
    subject: str
    preview_text: str
    html_content: str
    recipient_list: Optional[List[str]] = []
    send_time: Optional[str] = None

class MockGoogleAdsCampaign(BaseModel):
    campaign_name: str
    ad_group: Dict[str, Any]
    budget: float = 50.0
    bidding_strategy: str = "maximize_conversions"

@router.post("/facebook/posts")
async def create_facebook_post(post: MockFacebookPost):
    """Mock Facebook post creation"""
    post_id = f"fb_{uuid.uuid4().hex[:8]}"
    
    mock_campaigns[post_id] = {
        "type": "facebook",
        "content": post.dict(),
        "created_at": datetime.utcnow(),
        "metrics": {
            "impressions": 0,
            "clicks": 0,
            "engagement_rate": 0,
            "reactions": 0,
            "shares": 0,
            "comments": 0
        }
    }
    
    return {
        "post_id": post_id,
        "status": "published",
        "url": f"https://facebook.com/posts/{random.randint(100000, 999999)}",
        "published_at": datetime.utcnow().isoformat()
    }

@router.get("/facebook/insights/{post_id}")
async def get_facebook_insights(post_id: str):
    """Mock Facebook insights"""
    if post_id not in mock_campaigns:
        raise HTTPException(status_code=404, detail="Post not found")
    
    campaign = mock_campaigns[post_id]
    days_active = (datetime.utcnow() - campaign["created_at"]).days + 1
    
    impressions = random.randint(1000, 10000) * days_active
    engagement_rate = random.uniform(0.02, 0.08)
    
    return {
        "impressions": impressions,
        "clicks": int(impressions * random.uniform(0.01, 0.05)),
        "engagement_rate": engagement_rate,
        "conversion_rate": random.uniform(0.005, 0.03),
        "cost_per_action": random.uniform(5.0, 25.0),
        "reactions": int(impressions * random.uniform(0.005, 0.02)),
        "shares": int(impressions * random.uniform(0.001, 0.005)),
        "comments": int(impressions * random.uniform(0.0005, 0.002))
    }

@router.post("/email/campaigns")
async def create_email_campaign(campaign: MockEmailCampaign):
    """Mock email campaign creation"""
    campaign_id = f"email_{uuid.uuid4().hex[:8]}"
    
    mock_campaigns[campaign_id] = {
        "type": "email",
        "content": campaign.dict(),
        "created_at": datetime.utcnow(),
        "recipients": random.randint(1000, 5000)
    }
    
    return {
        "campaign_id": campaign_id,
        "status": "sent",
        "recipients": mock_campaigns[campaign_id]["recipients"],
        "sent_at": datetime.utcnow().isoformat()
    }

@router.get("/email/campaigns/{campaign_id}/stats")
async def get_email_stats(campaign_id: str):
    """Mock email campaign stats"""
    if campaign_id not in mock_campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = mock_campaigns[campaign_id]
    recipients = campaign["recipients"]
    
    open_rate = random.uniform(0.15, 0.35)
    click_rate = random.uniform(0.02, 0.08)
    
    opens = int(recipients * open_rate)
    clicks = int(opens * click_rate)
    
    return {
        "recipients": recipients,
        "opens": opens,
        "clicks": clicks,
        "open_rate": open_rate,
        "click_rate": click_rate,
        "conversion_rate": random.uniform(0.01, 0.05),
        "cost_per_acquisition": random.uniform(10.0, 50.0),
        "bounces": int(recipients * random.uniform(0.01, 0.03)),
        "unsubscribes": int(recipients * random.uniform(0.001, 0.005))
    }

@router.post("/google/campaigns")
async def create_google_campaign(campaign: MockGoogleAdsCampaign):
    """Mock Google Ads campaign creation"""
    campaign_id = f"google_{uuid.uuid4().hex[:8]}"
    
    mock_campaigns[campaign_id] = {
        "type": "google_ads",
        "content": campaign.dict(),
        "created_at": datetime.utcnow(),
        "daily_budget": campaign.budget
    }
    
    return {
        "campaign_id": campaign_id,
        "ad_group_id": f"adgroup_{random.randint(100000, 999999)}",
        "status": "active",
        "ads_created": len(campaign.ad_group.get("headlines", [])),
        "created_at": datetime.utcnow().isoformat()
    }

@router.get("/google/campaigns/{campaign_id}/metrics")
async def get_google_metrics(campaign_id: str):
    """Mock Google Ads metrics"""
    if campaign_id not in mock_campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = mock_campaigns[campaign_id]
    days_active = (datetime.utcnow() - campaign["created_at"]).days + 1
    daily_impressions = random.randint(500, 5000)
    
    impressions = daily_impressions * days_active
    ctr = random.uniform(0.02, 0.08)
    clicks = int(impressions * ctr)
    conversions = int(clicks * random.uniform(0.01, 0.04))
    
    return {
        "metrics": {
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "conversion_rate": conversions / clicks if clicks > 0 else 0,
            "cost_per_conversion": random.uniform(15.0, 75.0),
            "average_cpc": random.uniform(0.50, 3.00),
            "quality_score": random.randint(5, 10)
        }
    }