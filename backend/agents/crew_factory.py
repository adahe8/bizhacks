from crewai import Crew, Process
from typing import Dict, Any, List
import logging

from agents.content_agents.email_agent import create_email_content_agent
from agents.content_agents.facebook_agent import create_facebook_content_agent
from agents.content_agents.google_seo_agent import create_google_seo_content_agent
from agents.compliance_agent import create_compliance_agent
from agents.campaign_execution_agent import create_execution_agent

logger = logging.getLogger(__name__)

def create_campaign_crew(
    campaign_id: str,
    channel: str,
    product_info: Dict[str, Any],
    market_details: str,
    strategic_goals: str,
    guardrails: str
) -> Crew:
    """Create a crew for campaign execution"""
    
    # Select content agent based on channel
    if channel == "email":
        content_agent = create_email_content_agent(product_info, market_details)
    elif channel == "facebook":
        content_agent = create_facebook_content_agent(product_info, market_details)
    elif channel == "google_seo":
        content_agent = create_google_seo_content_agent(product_info, market_details)
    else:
        raise ValueError(f"Unsupported channel: {channel}")
    
    # Create compliance agent
    compliance_agent = create_compliance_agent(guardrails)
    
    # Create execution agent
    execution_agent = create_execution_agent(channel)
    
    # Create crew with sequential process
    crew = Crew(
        agents=[content_agent, compliance_agent, execution_agent],
        process=Process.sequential,
        verbose=True,
        max_iter=5  # Allow iterations for compliance feedback
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