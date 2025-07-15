# backend/agents/crew_factory.py
from crewai import Crew, Task, Agent
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Import all agent definitions
from .segmentation_agent import SegmentationAgent
from .campaign_creation_agent import CampaignCreationAgent
from .orchestrator_agent import OrchestratorAgent
from .content_agents import EmailContentAgent, FacebookContentAgent, GoogleAdsContentAgent
from .compliance_agent import ComplianceAgent
from .execution_agent import CampaignExecutionAgent
from .metrics_agent import MetricsGatherAgent

class CrewFactory:
    """Factory class to create and manage CrewAI crews"""
    
    def __init__(self):
        self.llm_api_key = os.getenv("OPENAI_API_KEY", "")
        
    def create_segmentation_crew(self, company_data: Dict[str, Any], customer_data: List[Dict]) -> Crew:
        """Create a crew for customer segmentation"""
        agent = SegmentationAgent(api_key=self.llm_api_key)
        
        task = Task(
            description=f"""
            Analyze the provided customer data and company information to create meaningful customer segments.
            
            Company Info:
            - Product: {company_data.get('product_name')}
            - Strategic Goals: {company_data.get('strategic_goals')}
            - Market Details: {company_data.get('market_details')}
            
            Create 3-5 distinct customer segments based on demographics, behavior, and purchase patterns.
            Each segment should have a clear name, description, and key characteristics.
            """,
            agent=agent.agent,
            expected_output="JSON list of customer segments with names, descriptions, and characteristics"
        )
        
        return Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=True
        )
    
    def create_campaign_generation_crew(self, company_data: Dict, segments: List[Dict]) -> Crew:
        """Create a crew for generating campaign ideas"""
        agent = CampaignCreationAgent(api_key=self.llm_api_key)
        
        tasks = []
        for segment in segments:
            task = Task(
                description=f"""
                Create innovative marketing campaign ideas for the following segment:
                
                Segment: {segment['name']}
                Description: {segment['description']}
                
                Company Product: {company_data.get('product_name')}
                Budget: ${company_data.get('monthly_budget')}
                Goals: {company_data.get('strategic_goals')}
                
                Generate 3-5 campaign ideas for each channel (Facebook, Email, Google Ads).
                Each campaign should have:
                - Name and description
                - Target frequency
                - Estimated budget allocation
                - Key messaging themes
                """,
                agent=agent.agent,
                expected_output="JSON list of campaign ideas with all required details"
            )
            tasks.append(task)
        
        return Crew(
            agents=[agent.agent],
            tasks=tasks,
            verbose=True
        )
    
    def create_content_generation_crew(self, campaign: Dict, channel: str, company_data: Dict) -> Crew:
        """Create a crew for content generation with compliance checking"""
        # Select appropriate content agent based on channel
        content_agents = {
            'facebook': FacebookContentAgent(api_key=self.llm_api_key),
            'email': EmailContentAgent(api_key=self.llm_api_key),
            'google_ads': GoogleAdsContentAgent(api_key=self.llm_api_key)
        }
        
        content_agent = content_agents.get(channel)
        compliance_agent = ComplianceAgent(api_key=self.llm_api_key)
        
        # Content generation task
        content_task = Task(
            description=f"""
            Create {channel} content for the following campaign:
            
            Campaign: {campaign['name']}
            Description: {campaign['description']}
            Theme: {campaign.get('theme', 'General')}
            
            Product: {company_data.get('product_name')}
            Brand Guidelines: {company_data.get('guardrails')}
            
            Generate engaging, on-brand content appropriate for {channel}.
            """,
            agent=content_agent.agent,
            expected_output=f"Complete {channel} content ready for publishing"
        )
        
        # Compliance review task
        compliance_task = Task(
            description=f"""
            Review the generated content for compliance with brand guidelines:
            
            Guidelines: {company_data.get('guardrails')}
            
            Check for:
            - Brand voice consistency
            - Appropriate messaging
            - Legal compliance
            - No prohibited content
            
            If non-compliant, provide specific feedback for revision.
            """,
            agent=compliance_agent.agent,
            expected_output="Compliance approval or specific revision requirements"
        )
        
        return Crew(
            agents=[content_agent.agent, compliance_agent.agent],
            tasks=[content_task, compliance_task],
            verbose=True
        )
    
    def create_orchestration_crew(self, campaigns: List[Dict], metrics: List[Dict]) -> Crew:
        """Create a crew for budget orchestration"""
        agent = OrchestratorAgent(api_key=self.llm_api_key)
        
        task = Task(
            description=f"""
            Analyze campaign performance metrics and reallocate budgets optimally.
            
            Current Campaigns: {len(campaigns)}
            
            Consider:
            - ROI and conversion rates
            - Cost per acquisition
            - Engagement metrics
            - Strategic goals alignment
            
            Provide new budget allocations for each campaign.
            """,
            agent=agent.agent,
            expected_output="JSON with campaign IDs and new budget allocations"
        )
        
        return Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=True
        )