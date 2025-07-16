# backend/agents/content_agents/email_agent.py

from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
import json
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

class EmailContent(BaseModel):
    """Pydantic model for email campaign content"""
    subject_line: str = Field(
        description="Compelling email subject line",
        min_length=10,
        max_length=50
    )
    preview_text: str = Field(
        description="Enticing preview text",
        min_length=20,
        max_length=90
    )
    greeting: str = Field(
        description="Personalized greeting",
        default="Hi {{first_name}},"
    )
    body_paragraphs: List[str] = Field(
        description="Main message paragraphs (2-3)",
        min_items=2,
        max_items=3
    )
    call_to_action: Dict[str, str] = Field(
        description="CTA with text and link",
        example={"text": "Shop Now", "link": "{{product_link}}"}
    )
    footer_text: str = Field(
        description="Footer with unsubscribe option",
        default="You're receiving this because you subscribed to our newsletter. {{unsubscribe_link}}"
    )
    send_time: str = Field(
        description="Optimal send time (HH:MM format)",
        pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    personalization_tokens: List[str] = Field(
        description="List of personalization tokens used",
        default=["{{first_name}}", "{{product_name}}", "{{discount_code}}"]
    )
    
    @validator('subject_line')
    def validate_subject_line(cls, v):
        if '!' in v and v.count('!') > 1:
            raise ValueError("Subject line should not be overly promotional (max 1 exclamation mark)")
        return v
    
    @property
    def body_html(self) -> str:
        """Generate full HTML body"""
        paragraphs_html = '\n'.join([f'<p>{p}</p>' for p in self.body_paragraphs])
        
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <p>{self.greeting}</p>
            {paragraphs_html}
            <div style="text-align: center; margin: 30px 0;">
                <a href="{self.call_to_action['link']}" 
                   style="background-color: #0ea5e9; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    {self.call_to_action['text']}
                </a>
            </div>
            <hr style="border: 1px solid #e5e5e5; margin: 30px 0;">
            <p style="font-size: 12px; color: #666; text-align: center;">
                {self.footer_text}
            </p>
        </div>
        """

def create_email_content_agent(
    product_info: Dict[str, Any],
    market_details: str
) -> Agent:
    """Create an agent for email content generation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7
    )
    
    agent = Agent(
        role="Email Marketing Specialist",
        goal="Create compelling email content that drives engagement and conversions",
        backstory=f"""You are an expert email marketer specializing in {product_info.get('name', 'beauty products')}.
        You understand email best practices, personalization, and how to craft messages that resonate
        with different customer segments. You know the market dynamics: {market_details}.
        You always structure your output according to the EmailContent model requirements.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[],
        output_pydantic=EmailContent
    )
    
    return agent

def create_email_content_task(agent: Agent, context: Dict[str, Any]) -> Task:
    """Create task for email content generation"""
    task = Task(
        description=f"""
        Create email marketing content for the campaign: {context.get('campaign_name')}
        
        Campaign Details:
        - Description: {context.get('campaign_description', 'N/A')}
        - Target Segment: {context.get('customer_segment', 'General Audience')}
        - Budget: ${context.get('budget', 0)}
        - Product: {context.get('product_name', 'Product')}
        - Strategic Goals: {context.get('strategic_goals', 'Increase sales')}
        
        Create compelling email content that includes:
        1. Subject line (compelling, under 50 characters, avoid spam triggers)
        2. Preview text (enticing, under 90 characters)
        3. Personalized greeting using merge tags
        4. Main message with 2-3 engaging paragraphs that:
           - Connect with the customer segment's needs
           - Highlight product benefits
           - Create urgency or excitement
        5. Clear call-to-action with button text and link placeholder
        6. Footer with unsubscribe option
        7. Optimal send time based on segment behavior
        8. List of personalization tokens to use
        
        The content should:
        - Align with the campaign goals and target segment
        - Use personalization effectively
        - Follow email marketing best practices
        - Be mobile-friendly and accessible
        
        Return the content following the EmailContent model structure.
        """,
        agent=agent,
        expected_output="Structured email content following EmailContent model",
        output_pydantic=EmailContent
    )
    
    return task