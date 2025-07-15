from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import logging

from core.config import settings

logger = logging.getLogger(__name__)

def create_email_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for email content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7
    )
    
    agent = Agent(
        role="Email Marketing Specialist",
        goal="Create compelling email content that drives engagement and conversions",
        backstory=f"""You are an expert email marketer specializing in {product_info.get('name', 'beauty products')}.
        You understand email best practices, personalization, and how to craft messages that resonate
        with different customer segments. You know the market dynamics: {market_details}""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    
    # Define the content generation task
    agent.task = Task(
        description="""
        Create email marketing content based on the campaign brief.
        
        Include:
        1. Subject line (compelling, under 50 characters)
        2. Preview text (enticing, under 90 characters)
        3. Email body with:
           - Personalized greeting
           - Main message (2-3 paragraphs)
           - Clear call-to-action
           - Footer with unsubscribe option
        4. Suggested send time
        
        The content should align with the campaign goals and target segment.
        Output as JSON with keys: subject_line, preview_text, body_html, send_time
        """,
        agent=agent,
        expected_output="JSON formatted email content"
    )
    
    return agent