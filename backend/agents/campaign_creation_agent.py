#  backend/agents/campaign_creation_agent.py
from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import json
import logging
import traceback

from backend.core.config import settings

logger = logging.getLogger(__name__)

def create_campaign_ideation_agent(
    segments: List[str],
    channels: List[str],
    strategic_goals: str,
    budget: float
) -> Agent:
    """Create an agent for campaign idea generation"""
    
    logger.debug(f"Creating campaign ideation agent...")
    logger.debug(f"GEMINI_API_KEY present: {bool(settings.GEMINI_API_KEY)}")
    logger.debug(f"GEMINI_API_KEY length: {len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.8
        )
        logger.debug("Successfully created ChatGoogleGenerativeAI instance")
    except Exception as e:
        logger.error(f"Failed to create ChatGoogleGenerativeAI: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    
    try:
        agent = Agent(
            role="Creative Campaign Strategist",
            goal="Generate innovative and effective campaign ideas that align with strategic goals",
            backstory="""You are a seasoned marketing strategist with expertise in creating
            multi-channel campaigns. You excel at matching campaign concepts to customer segments
            and optimizing budget allocation for maximum impact.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        logger.debug("Successfully created Agent instance")
        return agent
    except Exception as e:
        logger.error(f"Failed to create Agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def generate_campaign_ideas(
    segments: List[str],
    channels: List[str],
    strategic_goals: str,
    monthly_budget: float,
    campaign_count: int = 5
) -> List[Dict[str, Any]]:
    """Generate campaign ideas based on segments and channels"""
    
    logger.info("=== Starting campaign idea generation ===")
    logger.info(f"Segments: {segments}")
    logger.info(f"Channels: {channels}")
    logger.info(f"Strategic Goals: {strategic_goals}")
    logger.info(f"Monthly Budget: ${monthly_budget}")
    logger.info(f"Campaign Count: {campaign_count}")
    
    try:
        # Create agent
        logger.debug("Creating campaign ideation agent...")
        agent = create_campaign_ideation_agent(
            segments, channels, strategic_goals, monthly_budget
        )
        logger.debug("Agent created successfully")
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return default campaigns on agent creation failure
        logger.info("Falling back to default campaigns due to agent creation failure")
        return get_default_campaigns(segments, channels, monthly_budget, campaign_count)
    
    # Create ideation task
    try:
        logger.debug("Creating ideation task...")
        task = Task(
            description=f"""
            Create {campaign_count} innovative campaign ideas based on the following:
            
            Customer Segments: {', '.join(segments)}
            Available Channels: {', '.join(channels)}
            Strategic Goals: {strategic_goals}
            Total Monthly Budget: ${monthly_budget}
            
            For each campaign idea, provide:
            1. Campaign name (catchy and memorable)
            2. Description (2-3 sentences explaining the concept)
            3. Target channel (facebook, email, or google_seo)
            4. Target customer segment
            5. Suggested budget allocation (as percentage of total budget)
            6. Frequency (daily, weekly, or monthly)
            7. Key messaging points
            8. Expected outcomes
            
            Ensure campaigns are diverse, creative, and aligned with the strategic goals.
            Distribute campaigns across different segments and channels.
            Budget allocations should sum to approximately 100%.
            
            Return the campaigns as a JSON array.
            """,
            agent=agent,
            expected_output="JSON array of campaign ideas"
        )
        logger.debug("Task created successfully")
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return get_default_campaigns(segments, channels, monthly_budget, campaign_count)
    
    # Execute task
    try:
        logger.info("Executing task...")
        result = task.execute()
        logger.info(f"Task executed successfully. Result type: {type(result)}")
        logger.debug(f"Raw result: {result[:200]}..." if result else "Empty result")
    except Exception as e:
        logger.error(f"Failed to execute task: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return get_default_campaigns(segments, channels, monthly_budget, campaign_count)
    
    try:
        # Parse the result
        logger.debug("Attempting to parse result as JSON...")
        campaigns_data = json.loads(result)
        logger.info(f"Successfully parsed {len(campaigns_data)} campaigns from result")
        
        # Format campaigns
        campaigns = []
        budget_allocated = 0
        
        for i, campaign in enumerate(campaigns_data[:campaign_count]):
            logger.debug(f"Processing campaign {i+1}: {campaign.get('name', 'Unknown')}")
            
            budget_percent = campaign.get("budget_percentage", 20)
            campaign_budget = (budget_percent / 100) * monthly_budget
            budget_allocated += budget_percent
            
            campaigns.append({
                "name": campaign.get("name", ""),
                "description": campaign.get("description", ""),
                "channel": campaign.get("channel", "email"),
                "customer_segment": campaign.get("segment", segments[0] if segments else "General"),
                "suggested_budget": campaign_budget,
                "frequency": campaign.get("frequency", "weekly"),
                "messaging": campaign.get("messaging", []),
                "expected_outcomes": campaign.get("outcomes", "")
            })
        
        # Normalize budgets if they don't sum to 100%
        if budget_allocated != 100 and budget_allocated > 0:
            logger.debug(f"Normalizing budgets (allocated: {budget_allocated}%)")
            for campaign in campaigns:
                campaign["suggested_budget"] = (campaign["suggested_budget"] / budget_allocated) * monthly_budget
        
        logger.info(f"Successfully generated {len(campaigns)} campaign ideas")
        return campaigns
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse campaign ideas as JSON: {str(e)}")
        logger.error(f"Raw result: {result[:500]}..." if result else "Empty result")
        return get_default_campaigns(segments, channels, monthly_budget, campaign_count)
    except Exception as e:
        logger.error(f"Unexpected error processing campaigns: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return get_default_campaigns(segments, channels, monthly_budget, campaign_count)

def get_default_campaigns(
    segments: List[str],
    channels: List[str],
    monthly_budget: float,
    campaign_count: int
) -> List[Dict[str, Any]]:
    """Return default campaigns as fallback"""
    logger.info("Generating default campaigns as fallback...")
    default_campaigns = []
    budget_per_campaign = monthly_budget / campaign_count
    
    for i, channel in enumerate(channels[:campaign_count]):
        segment = segments[i % len(segments)] if segments else "General Audience"
        default_campaigns.append({
            "name": f"{channel.title()} Campaign {i+1}",
            "description": f"Targeted {channel} campaign for {segment}",
            "channel": channel,
            "customer_segment": segment,
            "suggested_budget": budget_per_campaign,
            "frequency": "weekly",
            "messaging": ["Quality products", "Customer satisfaction", "Special offers"],
            "expected_outcomes": "Increased engagement and conversions"
        })
    
    logger.info(f"Generated {len(default_campaigns)} default campaigns")
    return default_campaigns