# backend/services/orchestrator_service.py
from sqlmodel import Session, select
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any

from data.database import get_db_session
from data.models import Campaign, CampaignMetrics, CompanyDetails
from backend.agents.crew_factory import CrewFactory

logger = logging.getLogger(__name__)

class OrchestratorService:
    """Service for orchestrating budget rebalancing across campaigns"""
    
    @staticmethod
    async def rebalance_all_budgets():
        """Rebalance budgets for all running campaigns"""
        with get_db_session() as session:
            # Get company details for total budget
            company = session.exec(select(CompanyDetails)).first()
            if not company:
                logger.warning("No company setup found")
                return
            
            # Get all running campaigns
            campaigns = session.exec(
                select(Campaign).where(Campaign.status == "running")
            ).all()
            
            if not campaigns:
                logger.info("No running campaigns to rebalance")
                return
            
            # Gather recent metrics for each campaign
            campaign_performance = []
            for campaign in campaigns:
                metrics = session.exec(
                    select(CampaignMetrics)
                    .where(CampaignMetrics.campaign_id == campaign.id)
                    .order_by(CampaignMetrics.metric_date.desc())
                    .limit(7)  # Last 7 days
                ).all()
                
                if metrics:
                    # Calculate average performance
                    avg_roi = sum(m.roi for m in metrics) / len(metrics)
                    avg_ctr = sum(m.ctr for m in metrics) / len(metrics)
                    avg_conversions = sum(m.conversions for m in metrics) / len(metrics)
                    
                    campaign_performance.append({
                        'campaign_id': campaign.id,
                        'campaign_name': campaign.name,
                        'current_budget': campaign.current_budget,
                        'avg_roi': avg_roi,
                        'avg_ctr': avg_ctr,
                        'avg_conversions': avg_conversions,
                        'performance_score': OrchestratorService._calculate_performance_score(
                            avg_roi, avg_ctr, avg_conversions
                        )
                    })
            
            if not campaign_performance:
                logger.info("No campaign performance data available")
                return
            
            # Use AI to determine new budget allocations
            try:
                crew_factory = CrewFactory()
                crew = crew_factory.create_orchestration_crew(
                    campaigns=[c.dict() for c in campaigns],
                    metrics=campaign_performance
                )
                
                result = crew.kickoff()
                
                # For now, use a simple proportional allocation based on performance
                new_allocations = OrchestratorService._calculate_budget_allocations(
                    campaign_performance,
                    company.monthly_budget
                )
                
                # Apply new allocations
                for allocation in new_allocations:
                    campaign = session.get(Campaign, allocation['campaign_id'])
                    if campaign:
                        old_budget = campaign.current_budget
                        campaign.current_budget = allocation['new_budget']
                        campaign.updated_at = datetime.utcnow()
                        session.add(campaign)
                        
                        logger.info(
                            f"Rebalanced campaign {campaign.id}: "
                            f"${old_budget:.2f} -> ${allocation['new_budget']:.2f}"
                        )
                
                session.commit()
                logger.info(f"Successfully rebalanced budgets for {len(new_allocations)} campaigns")
                
            except Exception as e:
                logger.error(f"Error in budget rebalancing: {str(e)}")
    
    @staticmethod
    def _calculate_performance_score(roi: float, ctr: float, conversions: float) -> float:
        """Calculate a composite performance score"""
        # Weighted scoring: ROI (50%), Conversions (30%), CTR (20%)
        roi_score = min(roi * 10, 100)  # Cap at 100
        conversion_score = min(conversions / 10, 100)  # Normalize to 100
        ctr_score = min(ctr * 10, 100)  # Normalize to 100
        
        return (roi_score * 0.5) + (conversion_score * 0.3) + (ctr_score * 0.2)
    
    @staticmethod
    def _calculate_budget_allocations(
        campaign_performance: List[Dict[str, Any]], 
        total_budget: float
    ) -> List[Dict[str, Any]]:
        """Calculate new budget allocations based on performance"""
        # Calculate total performance score
        total_score = sum(cp['performance_score'] for cp in campaign_performance)
        
        if total_score == 0:
            # Equal distribution if no performance data
            equal_budget = total_budget / len(campaign_performance)
            return [
                {
                    'campaign_id': cp['campaign_id'],
                    'new_budget': equal_budget
                }
                for cp in campaign_performance
            ]
        
        # Allocate based on performance score
        allocations = []
        for cp in campaign_performance:
            # Ensure minimum budget of 10% and maximum of 40%
            proportion = cp['performance_score'] / total_score
            proportion = max(0.1, min(0.4, proportion))
            
            new_budget = total_budget * proportion
            
            allocations.append({
                'campaign_id': cp['campaign_id'],
                'new_budget': round(new_budget, 2)
            })
        
        # Adjust to ensure total equals monthly budget
        total_allocated = sum(a['new_budget'] for a in allocations)
        if total_allocated != total_budget:
            adjustment = (total_budget - total_allocated) / len(allocations)
            for allocation in allocations:
                allocation['new_budget'] += adjustment
                allocation['new_budget'] = round(allocation['new_budget'], 2)
        
        return allocations