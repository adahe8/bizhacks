# backend/services/scheduler_service.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
import logging

from data.database import engine
from data.models import Campaign, Schedule
from core.scheduler import scheduler, schedule_campaign_execution

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing campaign schedules"""
    
    @staticmethod
    def get_upcoming_schedules(days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming scheduled campaigns"""
        with Session(engine) as session:
            end_date = datetime.utcnow() + timedelta(days=days)
            
            schedules = session.exec(
                select(Schedule)
                .where(Schedule.scheduled_time <= end_date)
                .where(Schedule.status == "pending")
                .order_by(Schedule.scheduled_time)
            ).all()
            
            return [
                {
                    "schedule_id": schedule.id,
                    "campaign_id": schedule.campaign_id,
                    "campaign_name": schedule.campaign.name if schedule.campaign else "Unknown",
                    "scheduled_time": schedule.scheduled_time,
                    "job_id": schedule.job_id
                }
                for schedule in schedules
            ]
    
    @staticmethod
    def reschedule_failed_campaigns():
        """Reschedule campaigns that failed to execute"""
        with Session(engine) as session:
            # Find failed schedules from the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            failed_schedules = session.exec(
                select(Schedule)
                .where(Schedule.status == "failed")
                .where(Schedule.created_at >= yesterday)
            ).all()
            
            rescheduled = []
            for schedule in failed_schedules:
                # Create new schedule for 1 hour from now
                new_time = datetime.utcnow() + timedelta(hours=1)
                new_job_id = f"retry_{schedule.job_id}"
                
                new_schedule = Schedule(
                    campaign_id=schedule.campaign_id,
                    scheduled_time=new_time,
                    status="pending",
                    job_id=new_job_id
                )
                
                session.add(new_schedule)
                
                # Schedule with APScheduler
                schedule_campaign_execution(
                    schedule.campaign_id,
                    new_time,
                    new_job_id
                )
                
                rescheduled.append(schedule.campaign_id)
                
                # Mark old schedule as rescheduled
                schedule.status = "rescheduled"
                session.add(schedule)
            
            session.commit()
            
            if rescheduled:
                logger.info(f"Rescheduled {len(rescheduled)} failed campaigns")
            
            return rescheduled
    
    @staticmethod
    def cleanup_old_schedules(days: int = 30):
        """Clean up old completed/failed schedules"""
        with Session(engine) as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            old_schedules = session.exec(
                select(Schedule)
                .where(Schedule.created_at < cutoff_date)
                .where(Schedule.status.in_(["completed", "failed", "rescheduled"]))
            ).all()
            
            count = len(old_schedules)
            for schedule in old_schedules:
                session.delete(schedule)
            
            session.commit()
            
            if count > 0:
                logger.info(f"Cleaned up {count} old schedules")
            
            return count