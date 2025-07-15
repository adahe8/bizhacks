# backend/services/agent_service.py
from typing import List, Dict, Any
import json
import logging

from data.database import get_db_session
from data.models import CompanyDetails, CustomerSegment, Campaign
from backend.agents.crew_factory import CrewFactory

logger = logging.getLogger(__name__)

class AgentService:
    """Service for managing agent operations"""
    
    @staticmethod
    async def run_segmentation(company_id: int, customer_data: List[Dict]):
        """Run customer segmentation using AI agents"""
        with get_db_session() as session:
            company = session.get(CompanyDetails, company_id)
            if not company:
                raise ValueError("Company not found")
            
            crew_factory = CrewFactory()
            crew = crew_factory.create_segmentation_crew(
                company_data=company.dict(),
                customer_data=customer_data
            )
            
            # Execute crew
            result = crew.kickoff()
            
            # Parse results and save segments
            segments_data = json.loads(result) if isinstance(result, str) else result
            
            for seg_data in segments_data:
                segment = CustomerSegment(
                    name=seg_data['name'],
                    description=seg_data['description'],
                    characteristics=json.dumps(seg_data.get('characteristics', {})),
                    size_estimate=seg_data.get('size_estimate')
                )
                session.add(segment)
            
            session.commit()
            logger.info(f"Created {len(segments_data)} customer segments")
    
    @staticmethod
    async def generate_campaigns(company_id: int, segment_ids: List[int]):
        """Generate campaign ideas using AI"""
        with get_db_session() as session:
            company = session.get(CompanyDetails, company_id)
            segments = [session.get(CustomerSegment, sid) for sid in segment_ids]
            
            crew_factory = CrewFactory()
            crew = crew_factory.create_campaign_generation_crew(
                company_data=company.dict(),
                segments=[s.dict() for s in segments if s]
            )
            
            # Execute crew
            result = crew.kickoff()
            
            # Parse and save campaigns (but keep as drafts)
            campaigns_data = json.loads(result) if isinstance(result, str) else result
            
            for camp_data in campaigns_data:
                campaign = Campaign(
                    name=camp_data['name'],
                    description=camp_data['description'],
                    channel=camp_data['channel'],
                    segment_id=camp_data['segment_id'],
                    frequency_days=camp_data['frequency_days'],
                    assigned_budget=camp_data['budget'],
                    current_budget=camp_data['budget'],
                    theme=camp_data.get('theme'),
                    strategy=camp_data.get('strategy')
                )
                session.add(campaign)
            
            session.commit()
            logger.info(f"Generated {len(campaigns_data)} campaign ideas")
    
    @staticmethod
    async def rebalance_budgets(campaign_ids: List[int]):
        """Rebalance budgets across campaigns using AI"""
        with get_db_session() as session:
            from data.models import CampaignMetrics
            
            campaigns = [session.get(Campaign, cid) for cid in campaign_ids]
            
            # Get latest metrics for each campaign
            metrics = []
            for campaign in campaigns:
                if campaign:
                    latest_metrics = session.exec(
                        select(CampaignMetrics)
                        .where(CampaignMetrics.campaign_id == campaign.id)
                        .order_by(CampaignMetrics.metric_date.desc())
                        .limit(10)
                    ).all()
                    metrics.append({
                        'campaign_id': campaign.id,
                        'metrics': [m.dict() for m in latest_metrics]
                    })
            
            crew_factory = CrewFactory()
            crew = crew_factory.create_orchestration_crew(
                campaigns=[c.dict() for c in campaigns if c],
                metrics=metrics
            )
            
            # Execute crew
            result = crew.kickoff()
            
            # Apply new budget allocations
            allocations = json.loads(result) if isinstance(result, str) else result
            
            for alloc in allocations:
                campaign = session.get(Campaign, alloc['campaign_id'])
                if campaign:
                    campaign.current_budget = alloc['new_budget']
                    session.add(campaign)
            
            session.commit()
            logger.info(f"Rebalanced budgets for {len(allocations)} campaigns")