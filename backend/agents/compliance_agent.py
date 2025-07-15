from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import json
import logging

from core.config import settings

logger = logging.getLogger(__name__)

def create_compliance_agent(guardrails: str) -> Agent:
    """Create an agent for content compliance checking"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3  # Lower temperature for more consistent compliance checking
    )
    
    agent = Agent(
        role="Brand Compliance Officer",
        goal="Ensure all content adheres to brand guidelines and regulatory requirements",
        backstory=f"""You are a meticulous compliance specialist who ensures all marketing content
        meets brand standards and regulatory requirements. You review content against these guardrails:
        {guardrails}""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    
    return agent

def create_compliance_task(agent: Agent, guardrails: str) -> Task:
    """Create task for compliance checking"""
    task = Task(
        description=f"""
        Review the generated marketing content for compliance with brand guidelines and regulations.
        
        Guardrails to enforce:
        {guardrails}
        
        Check for:
        1. Brand voice consistency
        2. Factual accuracy
        3. Legal compliance (claims, disclaimers)
        4. Prohibited content or language
        5. Tone and messaging alignment
        
        If the content violates any guidelines, provide specific feedback on what needs to be changed.
        
        Provide:
        1. Compliance status (approved/rejected)
        2. Issues found (if any)
        3. Required changes (if rejected)
        4. Suggestions for improvement
        
        Output as JSON with keys: status, issues, required_changes, suggestions
        """,
        agent=agent,
        expected_output="JSON formatted compliance review"
    )
    
    return task

async def validate_content(content: Dict[str, Any], guardrails: str) -> Dict[str, Any]:
    """Validate content against brand guardrails"""
    
    agent = create_compliance_agent(guardrails)
    
    # Create validation task
    task = Task(
        description=f"""
        Review the following marketing content for compliance:
        
        Content: {json.dumps(content, indent=2)}
        
        Guardrails: {guardrails}
        
        Ensure the content meets all brand guidelines and regulatory requirements.
        Be thorough but fair in your assessment.
        """,
        agent=agent,
        expected_output="JSON formatted compliance review"
    )
    
    # Execute task
    result = task.execute()
    
    try:
        # Parse the result
        validation_result = json.loads(result)
        
        logger.info(f"Content validation result: {validation_result.get('status', 'unknown')}")
        return validation_result
        
    except json.JSONDecodeError:
        logger.error("Failed to parse validation result")
        return {
            "status": "error",
            "issues": ["Failed to parse compliance check result"],
            "required_changes": [],
            "suggestions": []
        }