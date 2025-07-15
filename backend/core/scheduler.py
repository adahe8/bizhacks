# backend/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor
from core.config import settings
import logging
from typing import Dict, Any
import pytz

logger = logging.getLogger(__name__)

# Configure job stores and executors
jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': AsyncIOExecutor(),
    'threadpool': ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_CAMPAIGNS)
}

job_defaults = {
    'coalesce': settings.SCHEDULER_JOB_DEFAULTS_COALESCE,
    'max_instances': settings.SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES,
    'misfire_grace_time': settings.SCHEDULER_MISFIRE_GRACE_TIME
}

# Create scheduler instance
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=pytz.timezone(settings.SCHEDULER_TIMEZONE)
)

def schedule_campaign_execution(campaign_id: str, schedule_time, job_id: str) -> str:
    """Schedule a campaign execution"""
    from backend.services.campaign_service import execute_campaign
    
    job = scheduler.add_job(
        execute_campaign,
        'date',
        run_date=schedule_time,
        args=[campaign_id],
        id=job_id,
        replace_existing=True,
        executor='threadpool'
    )
    
    logger.info(f"Scheduled campaign {campaign_id} for {schedule_time}")
    return job.id

def schedule_recurring_campaign(campaign_id: str, frequency: str, job_id: str) -> str:
    """Schedule a recurring campaign"""
    from backend.services.campaign_service import execute_campaign
    
    # Map frequency to APScheduler interval
    interval_map = {
        'daily': {'hours': 24},
        'weekly': {'weeks': 1},
        'monthly': {'weeks': 4}  # Approximate
    }
    
    interval = interval_map.get(frequency, {'hours': 24})
    
    job = scheduler.add_job(
        execute_campaign,
        'interval',
        **interval,
        args=[campaign_id],
        id=job_id,
        replace_existing=True,
        executor='threadpool'
    )
    
    logger.info(f"Scheduled recurring campaign {campaign_id} with frequency {frequency}")
    return job.id

def schedule_metrics_collection():
    """Schedule periodic metrics collection"""
    from agents.metrics_gather_agent import collect_all_metrics
    
    scheduler.add_job(
        collect_all_metrics,
        'interval',
        seconds=settings.METRICS_REFRESH_INTERVAL,
        id='metrics_collection',
        replace_existing=True
    )
    
    logger.info(f"Scheduled metrics collection every {settings.METRICS_REFRESH_INTERVAL} seconds")

def schedule_budget_rebalancing(frequency: str):
    """Schedule periodic budget rebalancing"""
    from agents.orchestrator_agent import rebalance_budgets
    
    interval_map = {
        'daily': {'hours': 24},
        'weekly': {'weeks': 1},
        'monthly': {'weeks': 4}
    }
    
    interval = interval_map.get(frequency, {'weeks': 1})
    
    scheduler.add_job(
        rebalance_budgets,
        'interval',
        **interval,
        id='budget_rebalancing',
        replace_existing=True
    )
    
    logger.info(f"Scheduled budget rebalancing with frequency {frequency}")

def cancel_job(job_id: str) -> bool:
    """Cancel a scheduled job"""
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Cancelled job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {str(e)}")
        return False

def get_job_info(job_id: str) -> Dict[str, Any]:
    """Get information about a scheduled job"""
    job = scheduler.get_job(job_id)
    if job:
        return {
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time,
            'trigger': str(job.trigger)
        }
    return {}

def initialize_scheduled_tasks():
    """Initialize default scheduled tasks"""
    # Schedule metrics collection
    schedule_metrics_collection()
    
    logger.info("Initialized default scheduled tasks")