from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
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
    
    # Define the content generation task
    agent.task = Task(
        description="""
        Create Facebook marketing content based on the campaign brief.
        
        Include:
        1. Primary text (engaging hook, main message, call-to-action)
        2. Headline (if using link format)
        3. Description (if using link format)
        4. Image suggestions (describe the ideal visual)
        5. Hashtags (3-5 relevant ones)
        6. Best posting time
        7. Audience targeting suggestions
        
        The content should be optimized for Facebook's algorithm and user behavior.
        Output as JSON with keys: primary_text, headline, description, image_description, hashtags, post_time, targeting
        """,
        agent=agent,
        expected_output="JSON formatted Facebook content"
    )
    
    return agent