"""
Initialize automated processes in the database
Should be run once when setting up the system
"""
from sqlalchemy.orm import Session
import os

from app.database.database import get_db
from app.database.automated_process_service import AutomatedProcessService
from app.database.models import TriggerTypeEnum
from shared.logger import get_logger

logger = get_logger(__name__)

# Timezone configuration
_TIMEZONE = os.getenv("BEHFLOW_TIMEZONE", "Asia/Tehran")


def initialize_automated_processes():
    """
    Initialize default automated processes in the database
    Creates the reschedule tasks process with default configuration
    """
    logger.info("Initializing automated processes")
    
    db: Session = next(get_db())
    
    try:
        # Check if reschedule process already exists
        existing = AutomatedProcessService.get_process_by_name(
            db=db,
            name="reschedule_remaining_tasks"
        )
        
        if existing:
            logger.info("Reschedule remaining tasks process already exists")
            
            # Update configuration if needed (from env vars)
            default_hour = int(os.getenv("RESCHEDULE_HOUR", "7"))
            default_minute = int(os.getenv("RESCHEDULE_MINUTE", "30"))
            
            new_schedule_config = {
                "hour": default_hour,
                "minute": default_minute,
                "timezone": _TIMEZONE
            }
            
            # Update if schedule config is different
            if existing.schedule_config != new_schedule_config:
                AutomatedProcessService.update_process(
                    db=db,
                    process_id=existing.process_id,
                    schedule_config=new_schedule_config
                )
                logger.info(f"Updated reschedule process schedule to {default_hour:02d}:{default_minute:02d}")
            
        else:
            # Create new reschedule process
            default_hour = int(os.getenv("RESCHEDULE_HOUR", "7"))
            default_minute = int(os.getenv("RESCHEDULE_MINUTE", "30"))
            
            process = AutomatedProcessService.create_process(
                db=db,
                name="reschedule_remaining_tasks",
                description="Reschedules incomplete tasks from previous days to the current day",
                trigger_type=TriggerTypeEnum.TIME_BASED,
                schedule_config={
                    "hour": default_hour,
                    "minute": default_minute,
                    "timezone": _TIMEZONE
                },
                process_config={
                    "include_statuses": ["pending", "in_progress"],
                    "update_to_today": True
                },
                is_enabled=True
            )
            
            logger.info(f"Created reschedule remaining tasks process (runs at {default_hour:02d}:{default_minute:02d})")
        
        logger.info("Automated processes initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing automated processes: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_automated_processes()
