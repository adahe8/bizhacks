# backend/external_apis/email_client.py
import random
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import uuid

class EmailClient:
    """Mock Email Service Provider API client"""
    
    def __init__(self):
        self.api_key = "mock_email_api_key"
        self.from_email = "marketing@company.com"
    
    async def send_campaign(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sending an email campaign"""
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        campaign_id = f"email_{uuid.uuid4().hex[:12]}"
        recipient_count = content_data.get("recipient_count", random.randint(1000, 10000))
        
        return {
            "id": campaign_id,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat(),
            "subject": content_data.get("subject", ""),
            "from": self.from_email,
            "recipient_count": recipient_count,
            "scheduled": False
        }
    
    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Simulate fetching email campaign metrics"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        sent = random.randint(5000, 20000)
        delivered = int(sent * random.uniform(0.95, 0.99))
        opened = int(delivered * random.uniform(0.15, 0.35))
        clicked = int(opened * random.uniform(0.10, 0.25))
        
        return {
            "campaign_id": campaign_id,
            "sent": sent,
            "delivered": delivered,
            "bounced": sent - delivered,
            "opened": opened,
            "clicked": clicked,
            "unsubscribed": random.randint(5, 50),
            "complained": random.randint(0, 5),
            "open_rate": round((opened / delivered) * 100, 2) if delivered > 0 else 0,
            "click_rate": round((clicked / delivered) * 100, 2) if delivered > 0 else 0,
            "ctr": round((clicked / opened) * 100, 2) if opened > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_subscriber_segments(self) -> List[Dict[str, Any]]:
        """Simulate fetching email subscriber segments"""
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        return [
            {
                "id": f"seg_{i}",
                "name": f"Segment {i}",
                "subscriber_count": random.randint(1000, 10000),
                "created_at": datetime.utcnow().isoformat()
            }
            for i in range(1, 6)
        ]
