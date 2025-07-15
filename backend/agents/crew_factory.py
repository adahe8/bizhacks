# backend/agents/crew_factory.py
from crewai import Crew, Process
from typing import Dict, Any, List, Union
from uuid import UUID
import logging
import json

from agents.content_agents.email_agent import create_email_content_agent, create_email_content_task
from agents.content_agents.facebook_agent import create_facebook_content_agent, create_facebook_content_task  
from agents.content_agents.google_seo_agent import create_google_seo_content_agent, create_google_seo_content_task
from agents.compliance_agent import create_compliance_agent, create_compliance_task
from agents.campaign_execution_agent import create_execution_agent, create_execution_task

logger = logging.getLogger(__name__)

def ensure_str(value: Union[str, UUID]) -> str:
    """Convert UUID to string if needed"""
    if isinstance(value, UUID):
        return str(value)
    return value

def create_campaign_crew(
    campaign_id: Union[str, UUID],
    channel: str,
    product_info: Dict[str, Any],
    market_details: str,
    strategic_goals: str,
    guardrails: str
) -> Crew:
    """Create a crew for campaign execution"""
    
    # Ensure campaign_id is string for crew context
    campaign_id_str = ensure_str(campaign_id)
    
    # Parse market details if it's a JSON string
    if isinstance(market_details, str):
        try:
            market_details_dict = json.loads(market_details)
            market_details_str = f"Target: {market_details_dict.get('target_demographics', 'N/A')}, Market Size: {market_details_dict.get('market_size', 'N/A')}"
        except:
            market_details_str = market_details
    else:
        market_details_str = str(market_details)
    
    # Create context for tasks
    context = {
        "campaign_id": campaign_id_str,
        "product_name": product_info.get("name", "Product"),
        "product_description": product_info.get("description", ""),
        "strategic_goals": strategic_goals,
        "market_details": market_details_str
    }
    
    # Select content agent based on channel
    if channel == "email":
        content_agent = create_email_content_agent(product_info, market_details_str)
        content_task = create_email_content_task(content_agent, context)
    elif channel == "facebook":
        content_agent = create_facebook_content_agent(product_info, market_details_str)
        content_task = create_facebook_content_task(content_agent, context)
    elif channel == "google_seo":
        content_agent = create_google_seo_content_agent(product_info, market_details_str)
        content_task = create_google_seo_content_task(content_agent, context)
    else:
        raise ValueError(f"Unsupported channel: {channel}")
    
    # Create compliance agent and task
    compliance_agent = create_compliance_agent(guardrails)
    compliance_task = create_compliance_task(compliance_agent, guardrails)
    
    # Create execution agent and task
    execution_agent = create_execution_agent(channel)
    execution_task = create_execution_task(execution_agent, channel, campaign_id_str)
    
    # Set task dependencies
    compliance_task.context = [content_task]
    execution_task.context = [compliance_task]
    
    # Create crew with sequential process
    crew = Crew(
        agents=[content_agent, compliance_agent, execution_agent],
        tasks=[content_task, compliance_task, execution_task],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info(f"Created campaign crew for {channel} channel")
    return crew

def create_segmentation_crew(
    product_info: Dict[str, Any],
    market_details: Dict[str, Any],
    user_data: List[Dict[str, Any]]
) -> Crew:
    """Create a crew for customer segmentation"""
    from agents.segmentation_agent import create_segmentation_agent
    
    segmentation_agent = create_segmentation_agent(product_info, market_details, user_data)
    
    crew = Crew(
        agents=[segmentation_agent],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Created segmentation crew")
    return crew

def create_campaign_ideation_crew(
    segments: List[str],
    channels: List[str],
    strategic_goals: str,
    budget: float
) -> Crew:
    """Create a crew for campaign idea generation"""
    from agents.campaign_creation_agent import create_campaign_ideation_agent
    
    ideation_agent = create_campaign_ideation_agent(
        segments, channels, strategic_goals, budget
    )
    
    crew = Crew(
        agents=[ideation_agent],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Created campaign ideation crew")
    return crew

def create_orchestration_crew() -> Crew:
    """Create a crew for budget orchestration and optimization"""
    from agents.orchestrator_agent import create_orchestrator_agent
    from agents.metrics_gather_agent import create_metrics_agent
    
    metrics_agent = create_metrics_agent()
    orchestrator_agent = create_orchestrator_agent()
    
    crew = Crew(
        agents=[metrics_agent, orchestrator_agent],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("Created orchestration crew")
    return crew