from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, timedelta
import json
import logging

from core.config import settings
from data.database import engine
from data.models import Campaign, Metric

logger = logging.getLogger(__name__)

def create_orchestrator_agent() -> Agent:
    """Create an agent for budget orchestration"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.5
    )
    
    agent = Agent(
        role="Budget Optimization Specialist",
        goal="Optimize budget allocation across campaigns based on performance metrics",
        backstory="""You are an expert in marketing analytics and budget optimization.
        You analyze campaign performance data and make data-driven decisions to maximize ROI
        by reallocating budgets to the most effective campaigns.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent

async def rebalance_budgets() -> List[Dict[str, Any]]:
    """Rebalance budgets across all active campaigns based on performance"""
    
    with Session(engine) as session:
        # Get all active campaigns
        active_campaigns = session.exec(
            select(Campaign).where(Campaign.status == "active")
        ).all()
        
        if not active_campaigns:
            logger.info("No active campaigns to rebalance")
            return []
        
        # Get metrics for each campaign from the last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        campaign_metrics = {}
        
        for campaign in active_campaigns:
            metrics = session.exec(
                select(Metric)
                .where(Metric.campaign_id == campaign.id)
                .where(Metric.timestamp >= week_ago)
            ).all()
            
            if metrics:
                # Calculate average performance
                avg_engagement = sum(m.engagement_rate or 0 for m in metrics) / len(metrics)
                avg_conversion = sum(m.conversion_rate or 0 for m in metrics) / len(metrics)
                avg_cpa = sum(m.cpa or 0 for m in metrics) / len(metrics)
                total_clicks = sum(m.clicks or 0 for m in metrics)
                
                campaign_metrics[str(campaign.id)] = {
                    "name": campaign.name,
                    "channel": campaign.channel,
                    "current_budget": campaign.budget,
                    "avg_engagement_rate": avg_engagement,
                    "avg_conversion_rate": avg_conversion,
                    "avg_cpa": avg_cpa,
                    "total_clicks": total_clicks,
                    "performance_score": (avg_engagement * 0.3 + avg_conversion * 0.5 - (avg_cpa / 100) * 0.2)
                }
            else:
                # No metrics yet, keep current budget
                campaign_metrics[str(campaign.id)] = {
                    "name": campaign.name,
                    "channel": campaign.channel,
                    "current_budget": campaign.budget,
                    "performance_score": 0.5  # Neutral score
                }
        
        # Create orchestrator agent
        agent = create_orchestrator_agent()
        
        # Get total budget
        total_budget = sum(c.budget for c in active_campaigns)
        
        # Create rebalancing task
        task = Task(
            description=f"""
            Analyze the performance metrics and reallocate the total budget of ${total_budget}
            across the active campaigns to maximize overall ROI.
            
            Campaign Performance Data:
            {json.dumps(campaign_metrics, indent=2)}
            
            Constraints:
            - Total budget must remain ${total_budget}
            - No campaign should receive less than ${settings.MIN_CAMPAIGN_BUDGET}
            - No campaign should receive more than {settings.MAX_BUDGET_ALLOCATION_PERCENT}% of total budget
            - Only make changes if performance difference exceeds {settings.REBALANCING_THRESHOLD * 100}%
            
            For each campaign, provide:
            1. campaign_id
            2. new_budget
            3. reason for change
            
            Return as a JSON array of budget allocations.
            """,
            agent=agent,
            expected_output="JSON array of budget allocations"
        )
        
        # Execute task
        result = task.execute()
        
        try:
            # Parse the result
            allocations = json.loads(result)
            
            rebalance_results = []
            
            for allocation in allocations:
                campaign_id = allocation.get("campaign_id")
                new_budget = allocation.get("new_budget", 0)
                reason = allocation.get("reason", "Performance-based adjustment")
                
                # Find the campaign
                campaign = next((c for c in active_campaigns if str(c.id) == campaign_id), None)
                if campaign and new_budget != campaign.budget:
                    old_budget = campaign.budget
                    
                    # Update campaign budget
                    campaign.budget = new_budget
                    campaign.updated_at = datetime.utcnow()
                    session.add(campaign)
                    
                    rebalance_results.append({
                        "campaign_id": campaign.id,
                        "old_budget": old_budget,
                        "new_budget": new_budget,
                        "reason": reason
                    })
                    
                    logger.info(f"Rebalanced campaign {campaign.name}: ${old_budget} -> ${new_budget}")
            
            session.commit()
            
            return rebalance_results
            
        except json.JSONDecodeError:
            logger.error("Failed to parse rebalancing results")
            return []
        except Exception as e:
            logger.error(f"Error during budget rebalancing: {str(e)}")
            session.rollback()
            return []