#!/usr/bin/env python3
"""
Script to examine scheduled jobs from the backend scheduler
Shows both APScheduler jobs and database Schedule records
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from data.database import engine
from data.models import Schedule, Campaign, Product
from backend.core.scheduler import scheduler
from backend.services.scheduler_service import SchedulerService
import json

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def print_separator(title: str = "", width: int = 80):
    """Print a separator line"""
    if title:
        print(f"\n{'=' * width}")
        print(f"{title.center(width)}")
        print('=' * width)
    else:
        print('-' * width)

def get_apscheduler_jobs():
    """Get all jobs from APScheduler"""
    try:
        # Initialize scheduler if not already running
        if not scheduler.running:
            print("Scheduler not running, starting it...")
            scheduler.start()
        
        jobs = scheduler.get_jobs()
        return jobs
    except Exception as e:
        print(f"Error accessing APScheduler: {e}")
        return []

def get_database_schedules():
    """Get all schedules from database"""
    schedules = []
    with Session(engine) as session:
        # Query schedules with related campaign info
        query = select(Schedule).order_by(Schedule.scheduled_time)
        db_schedules = session.exec(query).all()
        
        for schedule in db_schedules:
            # Fetch related campaign
            campaign = session.get(Campaign, schedule.campaign_id)
            product = None
            if campaign and campaign.product_id:
                product = session.get(Product, campaign.product_id)
            
            schedules.append({
                'schedule': schedule,
                'campaign': campaign,
                'product': product
            })
    
    return schedules

def print_apscheduler_jobs():
    """Print all APScheduler jobs"""
    print_separator("APSCHEDULER JOBS", 80)
    
    jobs = get_apscheduler_jobs()
    
    if not jobs:
        print("No jobs found in APScheduler")
        return
    
    print(f"Total jobs in scheduler: {len(jobs)}")
    print()
    
    for i, job in enumerate(jobs, 1):
        print(f"Job #{i}")
        print(f"  ID: {job.id}")
        print(f"  Name: {job.name}")
        print(f"  Function: {job.func_ref}")
        print(f"  Trigger: {job.trigger}")
        print(f"  Next run: {format_datetime(job.next_run_time)}")
        
        # Print job arguments
        if job.args:
            print(f"  Args: {job.args}")
        if job.kwargs:
            print(f"  Kwargs: {job.kwargs}")
        
        # Additional job details
        print(f"  Misfire grace time: {job.misfire_grace_time}")
        print(f"  Max instances: {job.max_instances}")
        print(f"  Coalesce: {job.coalesce}")
        
        print_separator("", 40)

def print_database_schedules():
    """Print all schedules from database"""
    print_separator("DATABASE SCHEDULES", 80)
    
    schedules = get_database_schedules()
    
    if not schedules:
        print("No schedules found in database")
        return
    
    print(f"Total schedules in database: {len(schedules)}")
    print()
    
    # Group by status
    status_groups = {}
    for item in schedules:
        status = item['schedule'].status
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(item)
    
    # Print schedules by status
    for status, items in status_groups.items():
        print(f"\n{status.upper()} Schedules ({len(items)}):")
        print_separator("", 60)
        
        for item in items:
            schedule = item['schedule']
            campaign = item['campaign']
            product = item['product']
            
            print(f"Schedule ID: {schedule.id}")
            print(f"  Status: {schedule.status}")
            print(f"  Scheduled Time: {format_datetime(schedule.scheduled_time)}")
            print(f"  Created At: {format_datetime(schedule.created_at)}")
            print(f"  Executed At: {format_datetime(schedule.executed_at)}")
            print(f"  Job ID: {schedule.job_id or 'None'}")
            
            if campaign:
                print(f"  Campaign: {campaign.name}")
                print(f"    Channel: {campaign.channel}")
                print(f"    Status: {campaign.status}")
                print(f"    Budget: ${campaign.budget}")
                
                if product:
                    print(f"    Product: {product.product_name}")
            
            print()

def check_schedule_consistency():
    """Check consistency between APScheduler and database"""
    print_separator("CONSISTENCY CHECK", 80)
    
    # Get jobs from both sources
    apscheduler_jobs = get_apscheduler_jobs()
    db_schedules = get_database_schedules()
    
    # Extract job IDs
    apscheduler_job_ids = {job.id for job in apscheduler_jobs}
    db_job_ids = {s['schedule'].job_id for s in db_schedules if s['schedule'].job_id}
    
    # Find discrepancies
    jobs_only_in_scheduler = apscheduler_job_ids - db_job_ids
    jobs_only_in_db = db_job_ids - apscheduler_job_ids
    jobs_in_both = apscheduler_job_ids & db_job_ids
    
    print(f"Jobs in APScheduler: {len(apscheduler_job_ids)}")
    print(f"Jobs referenced in DB: {len(db_job_ids)}")
    print(f"Jobs in both: {len(jobs_in_both)}")
    print()
    
    if jobs_only_in_scheduler:
        print(f"Jobs ONLY in APScheduler ({len(jobs_only_in_scheduler)}):")
        for job_id in jobs_only_in_scheduler:
            print(f"  - {job_id}")
    
    if jobs_only_in_db:
        print(f"\nJob IDs ONLY in Database ({len(jobs_only_in_db)}):")
        for job_id in jobs_only_in_db:
            print(f"  - {job_id}")

def print_scheduler_configuration():
    """Print scheduler configuration"""
    print_separator("SCHEDULER CONFIGURATION", 80)
    
    try:
        from backend.core.config import settings
        
        print(f"Timezone: {settings.SCHEDULER_TIMEZONE}")
        print(f"Job Coalesce: {settings.SCHEDULER_JOB_DEFAULTS_COALESCE}")
        print(f"Max Instances: {settings.SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES}")
        print(f"Misfire Grace Time: {settings.SCHEDULER_MISFIRE_GRACE_TIME} seconds")
        print(f"Max Concurrent Campaigns: {settings.MAX_CONCURRENT_CAMPAIGNS}")
        print(f"Campaign Retry Attempts: {settings.CAMPAIGN_RETRY_ATTEMPTS}")
        print(f"Campaign Retry Delay: {settings.CAMPAIGN_RETRY_DELAY} seconds")
        
    except Exception as e:
        print(f"Error loading configuration: {e}")

def get_execution_statistics():
    """Get statistics about schedule execution"""
    print_separator("EXECUTION STATISTICS", 80)
    
    with Session(engine) as session:
        # Count schedules by status
        status_counts = {}
        for status in ['pending', 'executing', 'completed', 'failed']:
            count = session.exec(
                select(Schedule).where(Schedule.status == status)
            ).all()
            status_counts[status] = len(count)
        
        print("Schedule Status Distribution:")
        for status, count in status_counts.items():
            print(f"  {status.capitalize()}: {count}")
        
        # Get recent executions
        print("\nRecent Executions (Last 10):")
        recent = session.exec(
            select(Schedule)
            .where(Schedule.executed_at.is_not(None))
            .order_by(Schedule.executed_at.desc())
            .limit(10)
        ).all()
        
        if recent:
            for schedule in recent:
                campaign = session.get(Campaign, schedule.campaign_id)
                print(f"  - {format_datetime(schedule.executed_at)}: "
                      f"{campaign.name if campaign else 'Unknown'} "
                      f"({schedule.status})")
        else:
            print("  No executed schedules found")
        
        # Get upcoming schedules
        print("\nUpcoming Schedules (Next 10):")
        upcoming = session.exec(
            select(Schedule)
            .where(Schedule.status == 'pending')
            .order_by(Schedule.scheduled_time)
            .limit(10)
        ).all()
        
        if upcoming:
            for schedule in upcoming:
                campaign = session.get(Campaign, schedule.campaign_id)
                print(f"  - {format_datetime(schedule.scheduled_time)}: "
                      f"{campaign.name if campaign else 'Unknown'} "
                      f"(Job ID: {schedule.job_id or 'Not scheduled'})")
        else:
            print("  No upcoming schedules found")

def main():
    """Main function"""
    print("=" * 80)
    print("SCHEDULER INSPECTION REPORT")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Print configuration
        print_scheduler_configuration()
        
        # Print APScheduler jobs
        print_apscheduler_jobs()
        
        # Print database schedules
        print_database_schedules()
        
        # Check consistency
        check_schedule_consistency()
        
        # Print statistics
        get_execution_statistics()
        
    except Exception as e:
        print(f"\nError during inspection: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)

if __name__ == "__main__":
    main()