# backend/external_apis/google_ads_client.py
import random
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import uuid

class GoogleAdsClient:
    """Mock Google Ads API client"""
    
    def __init__(self):
        self.customer_id = "123-456-7890"
        self.api_version = "v15"
    
    async def create_ad(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate creating a Google Ad"""
        await asyncio.sleep(random.uniform(0.8, 1.8))
        
        ad_id = f"gad_{uuid.uuid4().hex[:12]}"
        
        return {
            "id": ad_id,
            "campaign_id": content_data.get("campaign_id"),
            "ad_group_id": f"adg_{uuid.uuid4().hex[:8]}",
            "type": content_data.get("ad_type", "SEARCH"),
            "headline1": content_data.get("headline1", ""),
            "headline2": content_data.get("headline2", ""),
            "description": content_data.get("description", ""),
            "final_url": content_data.get("final_url", ""),
            "status": "ENABLED",
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_ad_performance(self, ad_id: str) -> Dict[str, Any]:
        """Simulate fetching ad performance metrics"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        impressions = random.randint(10000, 200000)
        clicks = int(impressions * random.uniform(0.02, 0.08))
        cost = clicks * random.uniform(0.50, 3.00)
        conversions = int(clicks * random.uniform(0.02, 0.10))
        
        return {
            "ad_id": ad_id,
            "impressions": impressions,
            "clicks": clicks,
            "cost": round(cost, 2),
            "conversions": conversions,
            "conversion_value": round(conversions * random.uniform(20, 100), 2),
            "ctr": round((clicks / impressions) * 100, 2) if impressions > 0 else 0,
            "avg_cpc": round(cost / clicks, 2) if clicks > 0 else 0,
            "conversion_rate": round((conversions / clicks) * 100, 2) if clicks > 0 else 0,
            "quality_score": random.randint(5, 10),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_keyword_ideas(self, seed_keywords: List[str]) -> List[Dict[str, Any]]:
        """Simulate fetching keyword ideas"""
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        keyword_ideas = []
        for seed in seed_keywords:
            for i in range(random.randint(3, 8)):
                keyword_ideas.append({
                    "keyword": f"{seed} {random.choice(['best', 'top', 'cheap', 'quality', 'review'])}",
                    "avg_monthly_searches": random.randint(100, 10000),
                    "competition": random.choice(["LOW", "MEDIUM", "HIGH"]),
                    "bid_range_low": round(random.uniform(0.20, 1.00), 2),
                    "bid_range_high": round(random.uniform(1.00, 5.00), 2)
                })
        
        return keyword_ideas
    
    async def update_budget(self, campaign_id: str, new_budget: float) -> Dict[str, Any]:
        """Simulate updating campaign budget"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        return {
            "campaign_id": campaign_id,
            "old_budget": random.uniform(100, 1000),
            "new_budget": new_budget,
            "status": "updated",
            "updated_at": datetime.utcnow().isoformat()
        }
