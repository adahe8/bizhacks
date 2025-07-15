
# backend/external_apis/facebook_client.py
import random
import asyncio
from datetime import datetime
from typing import Dict, Any
import uuid

class FacebookClient:
    """Mock Facebook API client"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.page_id = "mock_page_123"
    
    async def publish_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate publishing a Facebook post"""
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        post_id = f"fb_{uuid.uuid4().hex[:12]}"
        
        # Simulate response
        return {
            "id": post_id,
            "created_time": datetime.utcnow().isoformat(),
            "message": content_data.get("message", ""),
            "link": content_data.get("link"),
            "picture": content_data.get("image_url"),
            "status": "published"
        }
    
    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Simulate fetching post metrics"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Generate random metrics
        return {
            "post_id": post_id,
            "impressions": random.randint(1000, 50000),
            "reach": random.randint(800, 40000),
            "engagement": {
                "likes": random.randint(50, 2000),
                "comments": random.randint(5, 200),
                "shares": random.randint(2, 100)
            },
            "clicks": random.randint(100, 5000),
            "ctr": round(random.uniform(0.5, 5.0), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_ad_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Simulate fetching ad campaign metrics"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        spend = random.uniform(50, 500)
        clicks = random.randint(100, 2000)
        
        return {
            "campaign_id": campaign_id,
            "impressions": random.randint(5000, 100000),
            "clicks": clicks,
            "spend": round(spend, 2),
            "cpc": round(spend / clicks if clicks > 0 else 0, 2),
            "conversions": random.randint(10, 200),
            "conversion_rate": round(random.uniform(1.0, 10.0), 2),
            "timestamp": datetime.utcnow().isoformat()
        }