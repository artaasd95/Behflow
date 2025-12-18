"""
Scheduler module for automated processes
Uses APScheduler to run time-based automated processes
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.database.database import get_db
from app.database.automated_process_service import AutomatedProcessService
from app.database.automated_processes import get_process_executor
from app.database.models import TriggerTypeEnum, AutomatedProcessModel
from shared.logger import get_logger

logger = get_logger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance"""
    return _scheduler


def execute_process(process_id: str, process_name: str):
    """
    Execute an automated process
    
    Args:
        process_id: UUID of the process
        process_name: Name of the process to execute
    """
    logger.info(f"Executing automated process: {process_name}")
    
    try:
        # Get process executor
        executor_class = get_process_executor(process_name)
        if not executor_class:
            logger.error(f"No executor found for process: {process_name}")
            return
        
        # Get database session
        db: Session = next(get_db())
        
        try:
            # Execute the process
            result = executor_class.execute(db, process_id)
            
            if result.get("success"):
                logger.info(f"Process {process_name} completed successfully: {result}")
            else:
                logger.error(f"Process {process_name} failed: {result.get('error')}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error executing process {process_name}: {e}")


def schedule_process(scheduler: AsyncIOScheduler, process: AutomatedProcessModel):
    """
    Schedule a single automated process
    
    Args:
        scheduler: APScheduler instance
        process: Automated process model
    """
    if not process.is_enabled:
        logger.debug(f"Process {process.name} is disabled, skipping scheduling")
        return
    
    if process.trigger_type != TriggerTypeEnum.TIME_BASED:
        logger.debug(f"Process {process.name} is not time-based, skipping scheduling")
        return
    
    if not process.schedule_config:
        logger.warning(f"Process {process.name} has no schedule configuration")
        return
    
    try:
        # Extract schedule configuration
        hour = process.schedule_config.get("hour", 0)
        minute = process.schedule_config.get("minute", 0)
        timezone = process.schedule_config.get("timezone", os.getenv("BEHFLOW_TIMEZONE", "Asia/Tehran"))
        
        # Create cron trigger
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=timezone
        )
        
        # Add job to scheduler
        scheduler.add_job(
            execute_process,
            trigger=trigger,
            args=[str(process.process_id), process.name],
            id=str(process.process_id),
            name=process.name,
            replace_existing=True,
            coalesce=True,  # Combine missed runs
            max_instances=1  # Only one instance at a time
        )
        
        logger.info(f"Scheduled process '{process.name}' to run at {hour:02d}:{minute:02d} {timezone}")
        
    except Exception as e:
        logger.error(f"Error scheduling process {process.name}: {e}")


def initialize_scheduler() -> AsyncIOScheduler:
    """
    Initialize the scheduler and load all time-based processes
    
    Returns:
        AsyncIOScheduler instance
    """
    global _scheduler
    
    logger.info("Initializing automated process scheduler")
    
    # Create scheduler
    _scheduler = AsyncIOScheduler()
    
    try:
        # Get database session
        db: Session = next(get_db())
        
        try:
            # Load all time-based processes
            processes = AutomatedProcessService.get_processes_by_trigger_type(
                db=db,
                trigger_type=TriggerTypeEnum.TIME_BASED,
                enabled_only=True
            )
            
            logger.info(f"Found {len(processes)} time-based processes to schedule")
            
            # Schedule each process
            for process in processes:
                schedule_process(_scheduler, process)
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing scheduler: {e}")
    
    return _scheduler


def start_scheduler():
    """Start the scheduler"""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = initialize_scheduler()
    
    if _scheduler and not _scheduler.running:
        _scheduler.start()
        logger.info("Automated process scheduler started")
        
        # Log all scheduled jobs
        jobs = _scheduler.get_jobs()
        logger.info(f"Scheduled jobs: {len(jobs)}")
        for job in jobs:
            logger.info(f"  - {job.name}: next run at {job.next_run_time}")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global _scheduler
    
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("Automated process scheduler shutdown")
        _scheduler = None


def reload_schedules():
    """
    Reload all schedules from database.
    Useful when processes are updated.
    """
    global _scheduler
    
    if _scheduler is None:
        logger.warning("Scheduler not initialized")
        return
    
    logger.info("Reloading automated process schedules")
    
    try:
        # Remove all existing jobs
        _scheduler.remove_all_jobs()
        
        # Get database session
        db: Session = next(get_db())
        
        try:
            # Load all time-based processes
            processes = AutomatedProcessService.get_processes_by_trigger_type(
                db=db,
                trigger_type=TriggerTypeEnum.TIME_BASED,
                enabled_only=True
            )
            
            # Schedule each process
            for process in processes:
                schedule_process(_scheduler, process)
                
            logger.info(f"Reloaded {len(processes)} automated process schedules")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error reloading schedules: {e}")
