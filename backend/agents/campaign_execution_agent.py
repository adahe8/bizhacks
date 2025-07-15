# backend/agents/campaign_execution_agent.py
from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, Union
import json
import logging
from datetime import datetime
from uuid import UUID, uuid4

from backend.core.config import settings
from sqlmodel import Session
from data.database import engine
from data.models import ContentAsset, Campaign

logger = logging.getLogger(__name__)

def create_execution_agent(channel: str) -> Agent:
    """Create an agent for campaign execution"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )
    
    agent = Agent(
        role="Campaign Execution Specialist",
        goal=f"Execute and publish campaigns on {channel} platform",
        backstory=f"""You are an expert in executing marketing campaigns on {channel}.
        You handle the technical aspects of publishing content, managing assets, and ensuring
        successful campaign deployment.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    
    return agent

def create_execution_task(agent: Agent, channel: str, campaign_id: Union[str, UUID]) -> Task:
    """Create task for campaign execution"""
    # Ensure campaign_id is string for task description
    campaign_id_str = ensure_str(campaign_id)
    
    task = Task(
        description=f"""
        Execute the approved campaign content on {channel} platform.
        
        Campaign ID: {campaign_id_str}
        
        Steps to perform:
        1. Verify the content has been approved by compliance
        2. Prepare content for publication on {channel}
        3. Validate all required fields are present
        4. Schedule or publish immediately based on content recommendations
        5. Store content assets for future reference
        6. Return execution status and confirmation
        
        Output as JSON with keys: status, asset_id, published_at, platform_response
        """,
        agent=agent,
        expected_output="JSON formatted execution result"
    )
    
    return task

async def execute_campaign_content(
    campaign_id: Union[str, UUID],
    content: Dict[str, Any],
    channel: str
) -> Dict[str, Any]:
    """Execute campaign by publishing content to the specified channel"""
    
    # Ensure campaign_id is UUID for database operations
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
    
    try:
        # Publish content through the client
        publish_result = await client.publish_content(content)
        
        # Store content asset in database
        with Session(engine) as session:
            campaign = session.get(Campaign, campaign_uuid)
            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_uuid}")
            
            # Create content asset record
            asset = ContentAsset(
                campaign_id=campaign_uuid,
                platform=channel,
                asset_type="mixed",  # Could be text, image, video based on content
                copy_text=json.dumps(content),
                visual_url=publish_result.get("media_url"),
                status="published",
                published_at=datetime.utcnow()
            )
            
            session.add(asset)
            session.commit()
            
            logger.info(f"Content published for campaign {campaign.name} on {channel}")
            
            return {
                "status": "success",
                "asset_id": ensure_str(asset.id),
                "published_at": asset.published_at.isoformat(),
                "platform_response": publish_result
            }
            
    except Exception as e:
        logger.error(f"Error executing campaign on {channel}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "asset_id": None,
            "published_at": None,
            "platform_response": None
        }