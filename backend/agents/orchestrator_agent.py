from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize
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

def calculate_performance_score(metrics: List[Metric]) -> float:
    """Calculate performance score from metrics"""
    if not metrics:
        return 0.5  # Neutral score for new campaigns
    
    # Calculate weighted performance score
    total_impressions = sum(m.impressions or 0 for m in metrics)
    total_clicks = sum(m.clicks or 0 for m in metrics)
    avg_engagement = sum(m.engagement_rate or 0 for m in metrics) / len(metrics)
    avg_conversion = sum(m.conversion_rate or 0 for m in metrics) / len(metrics)
    avg_cpa = sum(m.cpa or 0 for m in metrics) / len(metrics)
    
    # Normalize CPA (lower is better)
    normalized_cpa = 1 / (1 + avg_cpa / 100) if avg_cpa > 0 else 0.5
    
    # Calculate CTR
    ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    
    # Weighted score
    score = (
        0.2 * ctr +
        0.3 * avg_engagement +
        0.3 * avg_conversion +
        0.2 * normalized_cpa
    )
    
    return score

def optimization_objective(budgets: np.ndarray, performance_scores: np.ndarray, total_budget: float) -> float:
    """Objective function to maximize performance while penalizing uneven distribution"""
    # Ensure budgets sum to total budget
    budgets = budgets * (total_budget / np.sum(budgets))
    
    # Performance component (negative because we minimize)
    performance = -np.sum(budgets * performance_scores)
    
    # Evenness penalty (standard deviation of budget distribution)
    mean_budget = total_budget / len(budgets)
    evenness_penalty = np.std(budgets - mean_budget) * settings.BUDGET_EVENNESS_PENALTY
    
    # Total objective
    objective = (
        settings.PERFORMANCE_WEIGHT * performance + 
        settings.EVENNESS_WEIGHT * evenness_penalty
    )
    
    return objective

async def rebalance_budgets() -> List[Dict[str, Any]]:
    """Rebalance budgets across all active campaigns using optimization"""
    
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
        campaign_data = []
        
        for campaign in active_campaigns:
            metrics = session.exec(
                select(Metric)
                .where(Metric.campaign_id == campaign.id)
                .where(Metric.timestamp >= week_ago)
            ).all()
            
            performance_score = calculate_performance_score(metrics)
            
            campaign_data.append({
                "campaign": campaign,
                "performance_score": performance_score,
                "current_budget": campaign.budget
            })
        
        # Extract data for optimization
        performance_scores = np.array([c["performance_score"] for c in campaign_data])
        current_budgets = np.array([c["current_budget"] for c in campaign_data])
        total_budget = np.sum(current_budgets)
        
        # Optimization constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}  # Sum equals total budget
        ]
        
        # Bounds for each campaign budget
        bounds = [(settings.MIN_CAMPAIGN_BUDGET, total_budget * settings.MAX_BUDGET_ALLOCATION_PERCENT / 100) 
                  for _ in campaign_data]
        
        # Run optimization
        result = minimize(
            optimization_objective,
            current_budgets,
            args=(performance_scores, total_budget),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            logger.error(f"Optimization failed: {result.message}")
            return []
        
        # Apply rebalancing results
        new_budgets = result.x
        rebalance_results = []
        
        for i, data in enumerate(campaign_data):
            campaign = data["campaign"]
            old_budget = campaign.budget
            new_budget = new_budgets[i]
            
            # Only update if change is significant
            change_ratio = abs(new_budget - old_budget) / old_budget
            if change_ratio > settings.REBALANCING_THRESHOLD:
                campaign.budget = new_budget
                campaign.updated_at = datetime.utcnow()
                session.add(campaign)
                
                reason = f"Performance score: {data['performance_score']:.3f}"
                if new_budget > old_budget:
                    reason += " - Increased due to strong performance"
                else:
                    reason += " - Decreased to reallocate to better performers"
                
                rebalance_results.append({
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "old_budget": old_budget,
                    "new_budget": new_budget,
                    "reason": reason
                })
                
                logger.info(f"Rebalanced campaign {campaign.name}: ${old_budget:.0f} -> ${new_budget:.0f}")
        
        session.commit()
        
        return rebalance_results