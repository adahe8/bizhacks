# backend/agents/campaign_creation_agent.py
from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from pydantic import BaseModel, Field, validator, ValidationError
import json
import logging
import traceback

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Pydantic models for output validation
class CampaignMessaging(BaseModel):
    """Messaging points for a campaign"""
    key_points: List[str] = Field(
        description="3-5 key messaging points",
        min_items=3,
        max_items=5
    )
    value_proposition: str = Field(
        description="Main value proposition"
    )
    call_to_action: str = Field(
        description="Primary call to action"
    )

class CampaignObjectives(BaseModel):
    """Specific objectives for a campaign"""
    primary_goal: str = Field(
        description="Primary campaign goal (e.g., increase brand awareness, drive sales, generate leads)"
    )
    target_metrics: Dict[str, float] = Field(
        description="Target metrics (e.g., {'engagement_rate': 0.05, 'conversion_rate': 0.02})"
    )
    success_criteria: List[str] = Field(
        description="Specific success criteria",
        min_items=2,
        max_items=4
    )

class CampaignIdea(BaseModel):
    """Model for a single campaign idea"""
    name: str = Field(
        description="Campaign name (catchy and memorable, 2-5 words)",
        min_length=5,
        max_length=50
    )
    description: str = Field(
        description="Campaign description (2-3 sentences)",
        min_length=50,
        max_length=300
    )
    channel: str = Field(
        description="Target channel",
        pattern="^(facebook|email|google_seo)$"
    )
    customer_segment: str = Field(
        description="Target customer segment name"
    )
    frequency: str = Field(
        description="Publishing frequency",
        pattern="^(daily|weekly|monthly)$"
    )
    budget_percentage: float = Field(
        description="Percentage of total budget (0-100)",
        ge=0,
        le=100
    )
    messaging: CampaignMessaging = Field(
        description="Campaign messaging details"
    )
    objectives: CampaignObjectives = Field(
        description="Specific campaign objectives"
    )
    expected_outcomes: str = Field(
        description="Expected outcomes and impact",
        min_length=50,
        max_length=200
    )
    
    @validator('name')
    def validate_name_uniqueness(cls, v):
        # Basic validation - actual uniqueness check happens at the list level
        if len(v.split()) > 5:
            raise ValueError("Campaign name should be 2-5 words")
        return v

class CampaignIdeaList(BaseModel):
    """Model for the list of campaign ideas"""
    campaigns: List[CampaignIdea] = Field(
        description="List of campaign ideas"
    )
    
    @validator('campaigns')
    def validate_unique_names(cls, v):
        names = [campaign.name for campaign in v]
        if len(names) != len(set(names)):
            raise ValueError("All campaign names must be unique")
        return v
    
    @validator('campaigns')
    def validate_budget_allocation(cls, v):
        total_budget = sum(campaign.budget_percentage for campaign in v)
        if not (95 <= total_budget <= 105):  # Allow 5% tolerance
            raise ValueError(f"Total budget allocation must be approximately 100%, got {total_budget}%")
        return v

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
            and optimizing budget allocation for maximum impact. You always provide structured
            output that follows exact specifications.""",
            llm=llm,
            verbose=True,
            allow_delegation=False,
            tools=[],
            output_pydantic=CampaignIdeaList  # Enable pydantic validation
        )
        logger.debug("Successfully created Agent instance with pydantic validation")
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
            
            Requirements for each campaign:
            1. UNIQUE campaign name (2-5 words, catchy and memorable) - NO DUPLICATES
            2. Description (2-3 sentences explaining the concept)
            3. Target channel (must be one of: facebook, email, or google_seo)
            4. Target customer segment (must be from provided segments)
            5. Publishing frequency (daily, weekly, or monthly)
            6. Budget percentage (as percentage of total budget)
            7. Detailed messaging including:
               - 3-5 key messaging points
               - Value proposition
               - Call to action
            8. Specific objectives including:
               - Primary goal (e.g., increase brand awareness, drive sales, generate leads)
               - Target metrics with specific numbers
               - 2-4 success criteria
            9. Expected outcomes (specific and measurable)
            
            IMPORTANT:
            - Campaigns must be diverse and target different segments/channels
            - Budget allocations must sum to approximately 100%
            - Each campaign must have a UNIQUE name
            - Be specific about objectives and expected outcomes
            - Align all campaigns with the strategic goals: {strategic_goals}
            
            Return the campaigns following the exact structure required by the CampaignIdeaList model.
            """,
            agent=agent,
            expected_output="Structured list of campaign ideas following CampaignIdeaList model",
            output_pydantic=CampaignIdeaList
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
        
        # If result is a CampaignIdeaList object, extract the data
        if isinstance(result, CampaignIdeaList):
            campaigns_data = result.campaigns
            logger.info(f"Successfully validated {len(campaigns_data)} campaigns")
        else:
            # Try to parse as JSON if string
            logger.debug("Result is not CampaignIdeaList, attempting JSON parse...")
            campaigns_list = json.loads(result) if isinstance(result, str) else result
            validated_list = CampaignIdeaList(campaigns=campaigns_list['campaigns'])
            campaigns_data = validated_list.campaigns
        
        # Format campaigns for response
        campaigns = []
        for campaign in campaigns_data[:campaign_count]:
            formatted_campaign = {
                "name": campaign.name,
                "description": campaign.description,
                "channel": campaign.channel,
                "customer_segment": campaign.customer_segment,
                "suggested_budget": (campaign.budget_percentage / 100) * monthly_budget,
                "frequency": campaign.frequency,
                "messaging": [
                    campaign.messaging.value_proposition,
                    *campaign.messaging.key_points
                ],
                "objectives": {
                    "primary_goal": campaign.objectives.primary_goal,
                    "target_metrics": campaign.objectives.target_metrics,
                    "success_criteria": campaign.objectives.success_criteria
                },
                "expected_outcomes": campaign.expected_outcomes
            }
            campaigns.append(formatted_campaign)
            logger.debug(f"Formatted campaign: {campaign.name}")
        
        logger.info(f"Successfully generated {len(campaigns)} campaign ideas")
        return campaigns
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse campaign ideas as JSON: {str(e)}")
        return get_default_campaigns(segments, channels, monthly_budget, campaign_count)
    except ValidationError as e:
        logger.error(f"Pydantic validation error: {str(e)}")
        logger.error(f"Validation errors: {e.errors()}")
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
    
    campaign_names = [
        "Summer Glow Campaign",
        "Radiant Beauty Drive", 
        "Natural Skincare Journey",
        "Premium Care Experience",
        "Beauty Boost Initiative"
    ]
    
    for i, channel in enumerate(channels[:campaign_count]):
        segment = segments[i % len(segments)] if segments else "General Audience"
        default_campaigns.append({
            "name": campaign_names[i % len(campaign_names)],
            "description": f"Targeted {channel} campaign designed to engage {segment} with personalized beauty content and exclusive offers.",
            "channel": channel,
            "customer_segment": segment,
            "suggested_budget": budget_per_campaign,
            "frequency": "weekly",
            "messaging": [
                "Discover your perfect skincare routine",
                "Natural ingredients for radiant skin", 
                "Personalized beauty solutions",
                "Limited time exclusive offers"
            ],
            "objectives": {
                "primary_goal": "Increase brand awareness and drive sales",
                "target_metrics": {
                    "engagement_rate": 0.05,
                    "conversion_rate": 0.02,
                    "click_through_rate": 0.03
                },
                "success_criteria": [
                    "Achieve 20% increase in engagement",
                    "Generate 50+ qualified leads per week"
                ]
            },
            "expected_outcomes": "20% increase in brand engagement and 15% boost in sales conversions within the target segment"
        })
    
    logger.info(f"Generated {len(default_campaigns)} default campaigns")
    return default_campaigns