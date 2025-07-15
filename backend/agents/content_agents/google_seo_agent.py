from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import logging

from core.config import settings

logger = logging.getLogger(__name__)

def create_google_seo_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for Google Ads/SEO content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.6
    )
    
    agent = Agent(
        role="SEO and Google Ads Specialist",
        goal="Create optimized content for Google Ads and SEO that drives qualified traffic",
        backstory=f"""You are an expert in Google Ads and SEO for {product_info.get('name', 'beauty products')}.
        You understand keyword research, ad copy optimization, and how to create content that ranks well
        and converts. You know the market: {market_details}""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    
    # Define the content generation task
    agent.task = Task(
        description="""
        Create Google Ads and SEO content based on the campaign brief.
        
        Include:
        1. Google Ads:
           - Headlines (3-5 variations, max 30 chars each)
           - Descriptions (2-3 variations, max 90 chars each)
           - Display URL paths
           - Keywords (10-15 relevant keywords)
           - Negative keywords (5-10)
        
        2. SEO Content:
           - Meta title (50-60 chars)
           - Meta description (150-160 chars)
           - H1 heading
           - Content outline (main topics to cover)
           - Target keywords with search intent
        
        Output as JSON with keys: ads_content, seo_content
        """,
        agent=agent,
        expected_output="JSON formatted Google Ads and SEO content"
    )
    
    return agent