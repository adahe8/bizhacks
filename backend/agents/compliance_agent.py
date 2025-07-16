# backend/agents/compliance_agent.py
from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import json
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

class ComplianceDecision(BaseModel):
    """Pydantic model for binary compliance decision"""
    approved: bool = Field(
        description="Whether the content is approved (True) or rejected (False)"
    )
    reason: str = Field(
        description="Brief reason for the decision",
        min_length=10,
        max_length=200
    )
    violations: List[str] = Field(
        description="List of specific guardrail violations if rejected",
        default=[]
    )
    
    @validator('violations')
    def validate_violations(cls, v, values):
        # If not approved, must have at least one violation
        if 'approved' in values and not values['approved'] and len(v) == 0:
            raise ValueError("Rejected content must specify at least one violation")
        # If approved, should not have violations
        if 'approved' in values and values['approved'] and len(v) > 0:
            raise ValueError("Approved content should not have violations")
        return v

def create_compliance_agent(guardrails: str) -> Agent:
    """Create an agent for content compliance checking"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.2  # Very low temperature for consistent binary decisions
    )
    
    agent = Agent(
        role="Brand Compliance Officer",
        goal="Make binary approval decisions on marketing content based on brand guidelines",
        backstory=f"""You are a strict compliance officer who reviews marketing content.
        You must make a clear YES/NO decision based on these guardrails:
        {guardrails}
        
        You APPROVE content only if it fully complies with ALL guardrails.
        You REJECT content if it violates ANY guardrail.
        Be decisive and provide clear reasoning.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=[],
        output_pydantic=ComplianceDecision
    )
    
    return agent

def create_compliance_task(agent: Agent, guardrails: str, content: Dict[str, Any]) -> Task:
    """Create task for compliance checking"""
    task = Task(
        description=f"""
        Review the marketing content and make a BINARY decision: APPROVE or REJECT.
        
        Content to Review:
        {json.dumps(content, indent=2)}
        
        Guardrails (ALL must be satisfied for approval):
        {guardrails}
        
        Make your decision based on:
        1. Does the content violate ANY of the guardrails? If yes, REJECT.
        2. Does the content fully comply with ALL guardrails? If yes, APPROVE.
        
        Check for:
        - Brand voice violations
        - Prohibited language or claims
        - Legal compliance issues
        - Tone inappropriateness
        - Factual inaccuracies
        - Any other guardrail violations
        
        Provide:
        - approved: true/false (binary decision)
        - reason: Brief explanation of your decision (10-200 characters)
        - violations: List of specific violations if rejected (empty list if approved)
        
        BE DECISIVE. No "maybe" or "needs revision" - only YES or NO.
        
        Return your decision following the ComplianceDecision model structure.
        """,
        agent=agent,
        expected_output="Binary compliance decision following ComplianceDecision model",
        output_pydantic=ComplianceDecision
    )
    
    return task

async def validate_content(content: Dict[str, Any], guardrails: str) -> Dict[str, Any]:
    """Validate content against brand guardrails with binary decision"""
    
    agent = create_compliance_agent(guardrails)
    task = create_compliance_task(agent, guardrails, content)
    
    try:
        # Execute task
        result = task.execute()
        
        # If result is a ComplianceDecision object, convert to dict
        if isinstance(result, ComplianceDecision):
            logger.info(f"Content validation decision: {'APPROVED' if result.approved else 'REJECTED'}")
            return {
                "status": "approved" if result.approved else "rejected",
                "approved": result.approved,
                "reason": result.reason,
                "violations": result.violations
            }
        else:
            # Try to parse as JSON if string
            decision = json.loads(result) if isinstance(result, str) else result
            logger.info(f"Content validation decision: {decision.get('approved', 'unknown')}")
            return {
                "status": "approved" if decision.get('approved', False) else "rejected",
                "approved": decision.get('approved', False),
                "reason": decision.get('reason', 'No reason provided'),
                "violations": decision.get('violations', [])
            }
            
    except json.JSONDecodeError:
        logger.error("Failed to parse validation result")
        return {
            "status": "error",
            "approved": False,
            "reason": "Failed to parse compliance check result",
            "violations": ["System error during validation"]
        }
    except Exception as e:
        logger.error(f"Error during content validation: {str(e)}")
        return {
            "status": "error", 
            "approved": False,
            "reason": f"Validation error: {str(e)}",
            "violations": ["System error during validation"]
        }