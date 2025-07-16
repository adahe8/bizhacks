#!/usr/bin/env python3
"""
Display all scheduled jobs in the system
Shows both database schedules and APScheduler jobs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from data.database import engine
from data.models import Schedule, Campaign
from backend.core.scheduler import scheduler
from datetime import datetime
from tabulate import tabulate
import asyncio

def get_database_schedules():
    """Get all schedules from the database"""
    with Session(engine) as session:
        # Query schedules with campaign information
        schedules = session.exec(
            select(Schedule, Campaign)
            .join(Campaign, Schedule.campaign_id == Campaign.id)
            .order_by(Schedule.scheduled_time)
        ).all()
        
        schedule_data = []
        for schedule, campaign in schedules:
            schedule_data.append({
                "Schedule ID": str(schedule.id)[:8],
                "Campaign": campaign.name,
                "Channel": campaign.channel,
                "Frequency": campaign.frequency,
                "Scheduled Time": schedule.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                "Status": schedule.status,
                "Job ID": schedule.job_id[:20] if schedule.job_id else "N/A",
                "Executed At": schedule.executed_at.strftime("%Y-%m-%d %H:%M") if schedule.executed_at else "Not executed"
            })
        
        return schedule_data

def get_apscheduler_jobs():
    """Get all jobs from APScheduler"""
    jobs = scheduler.get_jobs()
    
    job_data = []
    for job in jobs:
        job_data.append({
            "Job ID": job.id[:20],
            "Name": job.name,
            "Trigger": str(job.trigger),
            "Next Run": job.next_run_time.strftime("%Y-%m-%d %H:%M") if job.next_run_time else "N/A",
            "Executor": job.executor,
            "State": "Active" if job.next_run_time else "Paused"
        })
    
    return job_data

def print_schedule_summary():
    """Print summary statistics"""
    with Session(engine) as session:
        total_schedules = session.query(Schedule).count()
        pending_schedules = session.query(Schedule).filter(Schedule.status == "pending").count()
        completed_schedules = session.query(Schedule).filter(Schedule.status == "completed").count()
        failed_schedules = session.query(Schedule).filter(Schedule.status == "failed").count()
        
        active_campaigns = session.query(Campaign).filter(Campaign.status == "active").count()
        
        print("\n" + "="*60)
        print("SCHEDULE SUMMARY")
        print("="*60)
        print(f"Total Schedules: {total_schedules}")
        print(f"Pending: {pending_schedules}")
        print(f"Completed: {completed_schedules}")
        print(f"Failed: {failed_schedules}")
        print(f"Active Campaigns: {active_campaigns}")
        print("="*60 + "\n")

def print_upcoming_executions(days=7):
    """Print upcoming campaign executions"""
    from datetime import timedelta
    
    with Session(engine) as session:
        end_date = datetime.utcnow() + timedelta(days=days)
        
        upcoming = session.exec(
            select(Schedule, Campaign)
            .join(Campaign, Schedule.campaign_id == Campaign.id)
            .where(Schedule.scheduled_time <= end_date)
            .where(Schedule.scheduled_time >= datetime.utcnow())
            .where(Schedule.status == "pending")
            .order_by(Schedule.scheduled_time)
            .limit(10)
        ).all()
        
        if upcoming:
            print(f"\nNEXT 10 UPCOMING EXECUTIONS (Next {days} days)")
            print("-" * 80)
            for schedule, campaign in upcoming:
                days_until = (schedule.scheduled_time - datetime.utcnow()).days
                print(f"{schedule.scheduled_time.strftime('%Y-%m-%d %H:%M')} ({days_until} days) - {campaign.name} ({campaign.channel})")

async def main():
    """Main function"""
    print("\n" + "="*80)
    print("CAMPAIGN SCHEDULING SYSTEM - JOB INSPECTOR")
    print("="*80)
    print(f"Current Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Initialize scheduler if needed
    if not scheduler.running:
        scheduler.start()
    
    # Print summary
    print_schedule_summary()
    
    # Get and display database schedules
    print("\nDATABASE SCHEDULES")
    print("-" * 120)
    db_schedules = get_database_schedules()
    if db_schedules:
        print(tabulate(db_schedules, headers="keys", tablefmt="grid"))
    else:
        print("No schedules found in database")
    
    # Get and display APScheduler jobs
    print("\n\nAPSCHEDULER JOBS")
    print("-" * 120)
    scheduler_jobs = get_apscheduler_jobs()
    if scheduler_jobs:
        print(tabulate(scheduler_jobs, headers="keys", tablefmt="grid"))
    else:
        print("No jobs found in APScheduler")
    
    # Print upcoming executions
    print_upcoming_executions(days=7)
    
    # Print schedule distribution by frequency
    print("\n\nSCHEDULE DISTRIBUTION BY FREQUENCY")
    print("-" * 60)
    with Session(engine) as session:
        campaigns = session.query(Campaign).filter(Campaign.status == "active").all()
        freq_dist = {"daily": 0, "weekly": 0, "monthly": 0}
        for campaign in campaigns:
            if campaign.frequency in freq_dist:
                freq_dist[campaign.frequency] += 1
        
        for freq, count in freq_dist.items():
            print(f"{freq.capitalize()}: {count} campaigns")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    # Check if tabulate is installed
    try:
        import tabulate
    except ImportError:
        print("Please install tabulate: pip install tabulate")
        sys.exit(1)
    
    # Run the main function
    asyncio.run(main())