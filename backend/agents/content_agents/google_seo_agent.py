# backend/agents/content_agents/google_seo_agent.py
from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
import json
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

class GoogleAdHeadline(BaseModel):
    """Single headline for Google Ads"""
    text: str = Field(
        description="Headline text",
        min_length=5,
        max_length=30
    )
    include_keyword: bool = Field(
        description="Whether this headline includes a keyword",
        default=False
    )

class GoogleAdDescription(BaseModel):
    """Single description for Google Ads"""
    text: str = Field(
        description="Description text",
        min_length=10,
        max_length=90
    )
    include_benefits: bool = Field(
        description="Whether this description includes product benefits",
        default=True
    )

class GoogleAdsContent(BaseModel):
    """Content for Google Ads campaign"""
    headlines: List[GoogleAdHeadline] = Field(
        description="Ad headlines (3-5 variations)",
        min_items=3,
        max_items=5
    )
    descriptions: List[GoogleAdDescription] = Field(
        description="Ad descriptions (2-4 variations)",
        min_items=2,
        max_items=4
    )
    display_url: str = Field(
        description="Display URL path",
        max_length=30
    )
    final_url: str = Field(
        description="Landing page URL",
        default="{{landing_page_url}}"
    )
    
    @validator('headlines')
    def validate_headlines_diversity(cls, v):
        # Ensure at least one headline includes keyword placeholder
        if not any(headline.include_keyword for headline in v):
            raise ValueError("At least one headline must include a keyword")
        return v

class GoogleSeoContent(BaseModel):
    """Pydantic model for Google SEO/SEM campaign content"""
    campaign_name: str = Field(
        description="Campaign name for Google Ads",
        min_length=5,
        max_length=50
    )
    ad_group_name: str = Field(
        description="Ad group name",
        min_length=5,
        max_length=50
    )
    keywords: List[str] = Field(
        description="Target keywords (broad, phrase, exact match)",
        min_items=10,
        max_items=20
    )
    negative_keywords: List[str] = Field(
        description="Negative keywords to exclude",
        min_items=5,
        max_items=15
    )
    ads_content: GoogleAdsContent = Field(
        description="Google Ads content variations"
    )
    landing_page_recommendations: Dict[str, Any] = Field(
        description="SEO recommendations for landing page",
        default={
            "title_tag": "",
            "meta_description": "",
            "h1_tag": "",
            "content_keywords_density": "2-3%",
            "internal_links": 3,
            "cta_placement": "above_fold"
        }
    )
    bidding_strategy: str = Field(
        description="Recommended bidding strategy",
        pattern="^(maximize_clicks|maximize_conversions|target_cpa|target_roas)$"
    )
    daily_budget: float = Field(
        description="Recommended daily budget",
        gt=0
    )
    quality_score_factors: Dict[str, str] = Field(
        description="Factors to improve quality score",
        default={
            "relevance": "High keyword-to-ad relevance",
            "ctr": "Compelling headlines to improve CTR",
            "landing_page": "Fast, mobile-friendly, relevant content"
        }
    )
    
    @validator('keywords')
    def validate_keywords(cls, v):
        # Ensure mix of match types
        broad_count = sum(1 for k in v if not k.startswith('"') and not k.startswith('['))
        phrase_count = sum(1 for k in v if k.startswith('"') and k.endswith('"'))
        exact_count = sum(1 for k in v if k.startswith('[') and k.endswith(']'))
        
        if broad_count == 0 or phrase_count == 0 or exact_count == 0:
            raise ValueError("Keywords must include a mix of broad, phrase, and exact match types")
        return v

def create_google_seo_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for Google SEO/SEM content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.6
    )
    
    agent = Agent(
        role="Google Ads & SEO Specialist",
        goal="Create high-converting Google Ads campaigns and SEO-optimized content",
        backstory=f"""You are an expert in Google Ads and SEO for {product_info.get('name', 'beauty products')}.
        You understand keyword research, ad copywriting, quality score optimization, and how to create
        campaigns that deliver high ROI. You know the market: {market_details}.
        You always structure your output according to the GoogleSeoContent model requirements.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[],
        output_pydantic=GoogleSeoContent
    )
    
    return agent

def create_google_seo_content_task(agent: Agent, context: Dict[str, Any]) -> Task:
    """Create task for Google SEO/SEM content generation"""
    task = Task(
        description=f"""
        Create Google Ads campaign content for: {context.get('campaign_name')}
        
        Campaign Details:
        - Description: {context.get('campaign_description', 'N/A')}
        - Target Segment: {context.get('customer_segment', 'General Audience')}
        - Budget: ${context.get('budget', 0)}
        - Product: {context.get('product_name', 'Product')}
        - Strategic Goals: {context.get('strategic_goals', 'Increase online visibility')}
        
        Create comprehensive Google Ads content including:
        
        1. Campaign and ad group names (clear and organized)
        
        2. Keywords (10-20 total):
           - Mix of broad match (no symbols)
           - Phrase match (enclosed in quotes)
           - Exact match (enclosed in brackets)
           - Include high-intent commercial keywords
           - Include long-tail keywords
           
        3. Negative keywords (5-15) to prevent irrelevant clicks
        
        4. Ad content with:
           - 3-5 headline variations (max 30 chars each)
           - 2-4 description variations (max 90 chars each)
           - At least one headline with {{keyword}} placeholder
           - Clear value propositions
           - Strong calls-to-action
           
        5. Landing page SEO recommendations:
           - Optimized title tag
           - Meta description
           - H1 tag
           - Content keyword density
           - Internal linking strategy
           - CTA placement
           
        6. Bidding strategy recommendation based on goals
        
        7. Daily budget recommendation (based on monthly budget)
        
        8. Quality score optimization factors
        
        The content should:
        - Target high commercial intent
        - Align with user search behavior
        - Follow Google Ads policies
        - Optimize for quality score
        - Drive conversions efficiently
        
        Return the content following the GoogleSeoContent model structure.
        """,
        agent=agent,
        expected_output="Structured Google Ads content following GoogleSeoContent model",
        output_pydantic=GoogleSeoContent
    )
    
    return task