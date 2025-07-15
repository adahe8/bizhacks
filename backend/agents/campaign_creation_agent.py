from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import json
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

def create_campaign_ideation_agent(
    segments: List[str],
    channels: List[str],
    strategic_goals: str,
    budget: float
) -> Agent:
    """Create an agent for campaign idea generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.8
    )
    
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
    
    return agent

async def generate_campaign_ideas(
    segments: List[str],
    channels: List[str],
    strategic_goals: str,
    monthly_budget: float,
    campaign_count: int = 5
) -> List[Dict[str, Any]]:
    """Generate campaign ideas based on segments and channels"""
    
    # Create agent
    agent = create_campaign_ideation_agent(
        segments, channels, strategic_goals, monthly_budget
    )
    
    # Create ideation task
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
    
    # Execute task
    result = task.execute()
    
    try:
        # Parse the result
        campaigns_data = json.loads(result)
        
        # Format campaigns
        campaigns = []
        budget_allocated = 0
        
        for campaign in campaigns_data[:campaign_count]:
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
            for campaign in campaigns:
                campaign["suggested_budget"] = (campaign["suggested_budget"] / budget_allocated) * monthly_budget
        
        logger.info(f"Generated {len(campaigns)} campaign ideas")
        return campaigns
        
    except json.JSONDecodeError:
        logger.error("Failed to parse campaign ideas")
        # Return default campaigns
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
        
        return default_campaigns