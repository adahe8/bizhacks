from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import json
import logging

from core.config import settings

logger = logging.getLogger(__name__)

def create_facebook_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for Facebook content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.8
    )
    
    agent = Agent(
        role="Social Media Content Creator",
        goal="Create engaging Facebook content that drives social interaction and brand awareness",
        backstory=f"""You are a social media expert specializing in Facebook marketing for {product_info.get('name', 'beauty products')}.
        You understand what makes content shareable, how to use visuals effectively, and how to create posts
        that generate engagement. You know the market: {market_details}""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
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
        1. Primary text (engaging hook, main message, call-to-action)
        2. Headline (if using link format)
        3. Description (if using link format)
        4. Image suggestions (describe the ideal visual)
        5. Hashtags (3-5 relevant ones)
        6. Best posting time
        7. Audience targeting suggestions
        
        The content should be optimized for Facebook's algorithm and user behavior.
        Make it shareable, engaging, and visually appealing.
        
        Output as JSON with keys: primary_text, headline, description, image_description, hashtags, post_time, targeting
        """,
        agent=agent,
        expected_output="JSON formatted Facebook content"
    )
    
    return task