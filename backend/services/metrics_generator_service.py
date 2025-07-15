# backend/services/metrics_generator_service.py
import random
import numpy as np
from sqlmodel import Session, select
from datetime import datetime
from typing import Dict, Any
import json
import logging

from data.database import engine
from data.models import Campaign, CampaignMetrics, Metric
from core.config import settings

logger = logging.getLogger(__name__)

class MetricsGeneratorService:
    """Service for generating stochastic campaign metrics"""
    
    def __init__(self):
        self.channel_configs = settings.CHANNEL_METRICS
        
    def get_campaign_metrics_config(self, campaign_id: str) -> Dict[str, Any]:
        """Get or create unique metrics configuration for a campaign"""
        with Session(engine) as session:
            # Check if metrics config exists
            config = session.exec(
                select(CampaignMetrics).where(CampaignMetrics.campaign_id == campaign_id)
            ).first()
            
            if config:
                return json.loads(config.metrics_config)
            
            # Create new config with unique variance
            campaign = session.get(Campaign, campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")
            
            # Get base metrics for channel
            base_metrics = self.channel_configs.get(campaign.channel, {})
            
            # Apply random variance multiplier for uniqueness
            variance_mult = random.uniform(*settings.CAMPAIGN_VARIANCE_RANGE)
            
            unique_config = {}
            for metric_name, metric_config in base_metrics.items():
                unique_config[metric_name] = {
                    "mean": metric_config["base_mean"] * random.uniform(0.9, 1.1),
                    "variance": metric_config["base_variance"] * variance_mult,
                    "spend_coefficient": metric_config["spend_coefficient"],
                    "momentum": 0.0  # Track previous value for smoothing
                }
            
            # Save configuration
            campaign_metrics = CampaignMetrics(
                campaign_id=campaign_id,
                channel=campaign.channel,
                metrics_config=json.dumps(unique_config)
            )
            session.add(campaign_metrics)
            session.commit()
            
            return unique_config
    
    def generate_metrics(self, campaign_id: str, spend: float) -> Dict[str, float]:
        """Generate stochastic metrics for a campaign"""
        config = self.get_campaign_metrics_config(campaign_id)
        
        generated_metrics = {}
        
        for metric_name, metric_config in config.items():
            # Base value with spend influence
            base_value = metric_config["mean"] + (spend * metric_config["spend_coefficient"])
            
            # Add stochastic variation
            noise = np.random.normal(0, metric_config["variance"])
            
            # Apply momentum for smoothness (weighted average with previous)
            if metric_config["momentum"] > 0:
                value = 0.7 * base_value + 0.3 * metric_config["momentum"] + noise
            else:
                value = base_value + noise
            
            # Ensure non-negative and apply bounds
            if "rate" in metric_name or "conversion" in metric_name:
                value = max(0.001, min(1.0, value))  # Rates between 0.1% and 100%
            else:
                value = max(0, value)  # Non-negative for counts
            
            generated_metrics[metric_name] = value
            
            # Update momentum
            config[metric_name]["momentum"] = value
        
        # Update config with new momentum values
        self._update_metrics_config(campaign_id, config)
        
        return generated_metrics
    
    def _update_metrics_config(self, campaign_id: str, config: Dict[str, Any]):
        """Update metrics configuration"""
        with Session(engine) as session:
            campaign_metrics = session.exec(
                select(CampaignMetrics).where(CampaignMetrics.campaign_id == campaign_id)
            ).first()
            
            if campaign_metrics:
                campaign_metrics.metrics_config = json.dumps(config)
                session.add(campaign_metrics)
                session.commit()
    
    def calculate_reach(self, channel: str, metrics: Dict[str, float], impressions: int) -> float:
        """Calculate total reach based on channel and metrics"""
        if channel == "facebook":
            # Reach = impressions * engagement_rate * conversion_factor
            engagement = metrics.get("engagement_rate", 0.03)
            conversion = metrics.get("conversion_rate", 0.01)
            return impressions * engagement * (1 + conversion * 10)
            
        elif channel == "email":
            # Reach = impressions * open_rate * click_rate * conversion_factor
            open_rate = metrics.get("open_rate", 0.2)
            click_rate = metrics.get("click_rate", 0.025)
            conversion = metrics.get("conversion_rate", 0.015)
            return impressions * open_rate * click_rate * (1 + conversion * 15)
            
        elif channel == "google_seo":
            # Reach = impressions * CTR * quality_factor
            ctr = metrics.get("click_through_rate", 0.03)
            conversion = metrics.get("conversion_rate", 0.012)
            impressions_metric = metrics.get("impressions", impressions)
            return impressions_metric * ctr * (1 + conversion * 20)
            
        return impressions * 0.01  # Default
    
    async def generate_and_store_metrics(self, campaign_id: str) -> Metric:
        """Generate metrics and store in database"""
        with Session(engine) as session:
            campaign = session.get(Campaign, campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")
            
            # Generate metrics
            metrics_values = self.generate_metrics(campaign_id, campaign.budget)
            
            # Calculate impressions based on budget
            impressions = int(campaign.budget * random.uniform(100, 200))
            
            # Calculate reach
            reach = self.calculate_reach(campaign.channel, metrics_values, impressions)
            
            # Store metric
            metric = Metric(
                campaign_id=campaign_id,
                platform=campaign.channel,
                impressions=impressions,
                clicks=int(impressions * metrics_values.get("click_through_rate", 0.03)),
                engagement_rate=metrics_values.get("engagement_rate", metrics_values.get("open_rate", 0.03)),
                conversion_rate=metrics_values.get("conversion_rate", 0.01),
                cpa=campaign.budget / max(1, int(impressions * metrics_values.get("conversion_rate", 0.01))),
                timestamp=datetime.utcnow()
            )
            
            session.add(metric)
            session.commit()
            session.refresh(metric)
            
            # Update game state with reach
            from data.models import GameState
            game_state = session.exec(select(GameState).where(GameState.is_running == True)).first()
            if game_state:
                game_state.total_reach_optimal += reach
                # Non-optimal assumes equal distribution
                equal_budget_reach = reach * 0.85  # 15% less efficient
                game_state.total_reach_non_optimal += equal_budget_reach
                game_state.updated_at = datetime.utcnow()
                session.add(game_state)
                session.commit()
            
            logger.info(f"Generated metrics for campaign {campaign.name}: Reach={reach:.0f}")
            return metric