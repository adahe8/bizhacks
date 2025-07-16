# backend/external_apis/email_client.py
import httpx
from typing import Dict, Any
from datetime import datetime
import random
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

class EmailClient:
    """Client for Email Service API (Mock Implementation)"""
    
    def __init__(self):
        self.api_endpoint = settings.EMAIL_SERVICE_API_ENDPOINT
        self.api_key = settings.EMAIL_SERVICE_API_KEY
    
    async def publish_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send email campaign"""
        
        try:
            if self.api_endpoint.startswith("http://localhost"):
                # Mock response for development
                return {
                    "campaign_id": f"email_{datetime.utcnow().timestamp()}",
                    "status": "sent",
                    "recipients": random.randint(1000, 5000),
                    "scheduled_time": content.get("send_time"),
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                # Real API call (e.g., SendGrid, Mailchimp)
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.api_endpoint}/campaigns",
                        json={
                            "subject": content.get("subject_line", ""),
                            "preview_text": content.get("preview_text", ""),
                            "html_content": content.get("body_html", ""),
                            "recipient_list": content.get("recipients", []),
                            "send_time": content.get("send_time")
                        },
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        }
                    )
                    response.raise_for_status()
                    return response.json()
                    
        except Exception as e:
            logger.error(f"Error sending email campaign: {str(e)}")
            raise
    
    async def get_metrics(self, asset_id: str, published_at: datetime = None) -> Dict[str, Any]:
        """Get email campaign metrics"""
        
        try:
            if self.api_endpoint.startswith("http://localhost"):
                # Mock metrics for development
                days_since_send = (datetime.utcnow() - published_at).days if published_at else 1
                recipients = random.randint(1000, 5000)
                
                open_rate = random.uniform(0.15, 0.35)
                click_rate = random.uniform(0.02, 0.08)
                
                opens = int(recipients * open_rate)
                clicks = int(opens * click_rate)
                
                return {
                    "asset_id": asset_id,
                    "impressions": recipients,  # Total recipients
                    "clicks": clicks,
                    "engagement_rate": open_rate,  # Open rate for emails
                    "conversion_rate": random.uniform(0.01, 0.05),
                    "cpa": random.uniform(10.0, 50.0),
                    "opens": opens,
                    "bounces": int(recipients * random.uniform(0.01, 0.03)),
                    "unsubscribes": int(recipients * random.uniform(0.001, 0.005))
                }
            else:
                # Real API call
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.api_endpoint}/campaigns/{asset_id}/stats",
                        headers={
                            "Authorization": f"Bearer {self.api_key}"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Process and return metrics
                    return {
                        "asset_id": asset_id,
                        "impressions": data.get("recipients", 0),
                        "clicks": data.get("clicks", 0),
                        "engagement_rate": data.get("open_rate", 0),
                        "conversion_rate": data.get("conversion_rate", 0),
                        "cpa": data.get("cost_per_acquisition", 0),
                        "opens": data.get("opens", 0),
                        "bounces": data.get("bounces", 0),
                        "unsubscribes": data.get("unsubscribes", 0)
                    }
                    
        except Exception as e:
            logger.error(f"Error getting email metrics: {str(e)}")
            raise
