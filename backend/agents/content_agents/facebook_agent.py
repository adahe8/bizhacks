# backend/agents/content_agents/facebook_agent.py
from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import json
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

class FacebookTargeting(BaseModel):
    """Targeting parameters for Facebook ads"""
    age_min: int = Field(ge=18, le=65, description="Minimum age")
    age_max: int = Field(ge=18, le=65, description="Maximum age")
    genders: List[str] = Field(
        description="Target genders",
        default=["all"]
    )
    interests: List[str] = Field(
        description="Interest targeting",
        min_items=3,
        max_items=10
    )
    behaviors: List[str] = Field(
        description="Behavioral targeting",
        min_items=1,
        max_items=5
    )
    custom_audiences: List[str] = Field(
        description="Custom audience names",
        default=[]
    )

class FacebookContent(BaseModel):
    """Pydantic model for Facebook campaign content"""
    primary_text: str = Field(
        description="Main post text with engaging hook",
        min_length=50,
        max_length=500
    )
    headline: str = Field(
        description="Attention-grabbing headline",
        min_length=10,
        max_length=40
    )
    description: str = Field(
        description="Supporting description",
        min_length=20,
        max_length=90
    )
    call_to_action: str = Field(
        description="CTA button text",
        pattern="^(Shop Now|Learn More|Sign Up|Get Offer|Contact Us|Download|Watch More)$"
    )
    link: str = Field(
        description="Landing page URL",
        default="{{landing_page_url}}"
    )
    hashtags: List[str] = Field(
        description="Relevant hashtags (3-5)",
        min_items=3,
        max_items=5
    )
    image_specs: Dict[str, Any] = Field(
        description="Ideal image specifications",
        default={
            "type": "product_lifestyle",
            "aspect_ratio": "1:1",
            "text_overlay": "minimal",
            "brand_elements": True
        }
    )
    post_time: str = Field(
        description="Optimal posting time (HH:MM format)",
        pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    targeting: FacebookTargeting = Field(
        description="Audience targeting parameters"
    )
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        for tag in v:
            if not tag.startswith('#'):
                raise ValueError(f"Hashtag must start with #: {tag}")
            if len(tag) > 30:
                raise ValueError(f"Hashtag too long: {tag}")
        return v
    
    @validator('primary_text')
    def validate_primary_text(cls, v):
        # Check for engaging start
        first_sentence = v.split('.')[0]
        if len(first_sentence) > 100:
            raise ValueError("First sentence should be punchy and under 100 characters")
        return v

def create_facebook_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for Facebook content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.8
    )
    
    agent = Agent(
        role="Social Media Content Creator",
        goal="Create engaging Facebook content that drives social interaction and brand awareness",
        backstory=f"""You are a social media expert specializing in Facebook marketing for {product_info.get('name', 'beauty products')}.
        You understand what makes content shareable, how to use visuals effectively, and how to create posts
        that generate engagement. You know the market: {market_details}.
        You always structure your output according to the FacebookContent model requirements.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[],
        output_pydantic=FacebookContent
    )
    
    return agent

def create_facebook_content_task(agent: Agent, context: Dict[str, Any]) -> Task:
    """Create task for Facebook content generation"""
    task = Task(
        description=f"""
        Create Facebook marketing content for the campaign: {context.get('campaign_name')}
        
        Campaign Details:
        - Description: {context.get('campaign_description', 'N/A')}
        - Target Segment: {context.get('customer_segment', 'General Audience')}
        - Budget: ${context.get('budget', 0)}
        - Product: {context.get('product_name', 'Product')}
        - Strategic Goals: {context.get('strategic_goals', 'Increase brand awareness')}
        
        Create engaging Facebook content that includes:
        1. Primary text with:
           - Attention-grabbing opening hook
           - Value proposition
           - Social proof or urgency
           - Clear call-to-action
        2. Compelling headline (under 40 characters)
        3. Supporting description
        4. Appropriate CTA button (Shop Now, Learn More, etc.)
        5. Landing page link placeholder
        6. 3-5 relevant hashtags that are:
           - Popular but not oversaturated
           - Specific to the product/campaign
           - Include branded hashtag
        7. Image specifications describing the ideal visual
        8. Optimal posting time based on audience behavior
        9. Detailed targeting parameters including:
           - Age range
           - Interests (3-10)
           - Behaviors (1-5)
           - Custom audiences if applicable
        
        The content should:
        - Be optimized for Facebook's algorithm
        - Encourage engagement (likes, comments, shares)
        - Use visual storytelling principles
        - Align with the target segment's preferences
        - Follow Facebook advertising policies
        
        Return the content following the FacebookContent model structure.
        """,
        agent=agent,
        expected_output="Structured Facebook content following FacebookContent model",
        output_pydantic=FacebookContent
    )
    
    return task