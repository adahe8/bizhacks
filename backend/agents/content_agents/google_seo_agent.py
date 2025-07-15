from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import json
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

def create_google_seo_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for Google Ads/SEO content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
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
    
    return agent

def create_google_seo_content_task(agent: Agent, context: Dict[str, Any]) -> Task:
    """Create task for Google SEO/Ads content generation"""
    task = Task(
        description=f"""
        Create Google Ads and SEO content for the campaign: {context.get('campaign_name')}
        
        Campaign Details:
        - Description: {context.get('campaign_description', 'N/A')}
        - Target Segment: {context.get('customer_segment', 'General Audience')}
        - Budget: ${context.get('budget', 0)}
        - Product: {context.get('product_name', 'Product')}
        - Strategic Goals: {context.get('strategic_goals', 'Drive qualified traffic')}
        
        Create optimized Google Ads content that includes:
        1. Google Ads:
           - Headlines (3-5 variations, max 30 chars each)
           - Descriptions (2-3 variations, max 90 chars each)
           - Display URL paths
           - Keywords (10-15 relevant keywords with high commercial intent)
           - Negative keywords (5-10 to exclude irrelevant traffic)
        
        2. SEO Content:
           - Meta title (50-60 chars)
           - Meta description (150-160 chars)
           - H1 heading
           - Content outline (main topics to cover)
           - Target keywords with search intent
        
        Focus on keywords that indicate buying intent and match the target segment.
        
        Output as JSON with keys: ads_content (containing headlines, descriptions, keywords, negative_keywords), seo_content (containing meta_title, meta_description, h1, outline, target_keywords)
        """,
        agent=agent,
        expected_output="JSON formatted Google Ads and SEO content"
    )
    
    return task