# backend/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure scheduler
jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone='UTC',
    job_defaults={
        'coalesce': True,
        'max_instances': 3
    }
)

def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

def schedule_campaign(campaign_id: int, frequency_days: int):
    """Schedule a campaign for periodic execution"""
    from backend.services.campaign_service import CampaignService
    
    job_id = f"campaign_{campaign_id}"
    
    # Remove existing job if any
    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)
    
    # Schedule new job
    scheduler.add_job(
        CampaignService.execute_campaign,
        'interval',
        days=frequency_days,
        id=job_id,
        args=[campaign_id],
        next_run_time=datetime.utcnow() + timedelta(minutes=1)  # Start soon
    )
    
    logger.info(f"Scheduled campaign {campaign_id} to run every {frequency_days} days")

def schedule_metrics_gathering():
    """Schedule periodic metrics gathering"""
    from backend.services.metrics_service import MetricsService
    
    scheduler.add_job(
        MetricsService.gather_all_metrics,
        'interval',
        hours=6,  # Every 6 hours
        id='metrics_gathering',
        next_run_time=datetime.utcnow() + timedelta(minutes=30)
    )
    
    logger.info("Scheduled metrics gathering every 6 hours")

def schedule_budget_rebalancing(frequency_days: int = 7):
    """Schedule periodic budget rebalancing"""
    from backend.services.orchestrator_service import OrchestratorService
    
    scheduler.add_job(
        OrchestratorService.rebalance_all_budgets,
        'interval',
        days=frequency_days,
        id='budget_rebalancing',
        next_run_time=datetime.utcnow() + timedelta(days=frequency_days)
    )
    
    logger.info(f"Scheduled budget rebalancing every {frequency_days} days")