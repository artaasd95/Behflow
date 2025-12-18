"""
Automated Processes Implementations
Contains the actual logic for various automated processes
"""
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from typing import Dict, Any, List
import os

import pytz
import jdatetime

from app.database.models import TaskModel, StatusEnum
from app.database.automated_process_service import AutomatedProcessService
from app.database.models import ProcessStatusEnum
from shared.logger import get_logger

logger = get_logger(__name__)

# Timezone configuration
_TIMEZONE = os.getenv("BEHFLOW_TIMEZONE", "Asia/Tehran")
_TZ = pytz.timezone(_TIMEZONE)


def _to_jalali_iso(dt: datetime) -> str:
    """Convert a timezone-aware Gregorian datetime to a Jalali ISO string."""
    if dt.tzinfo is None:
        dt = _TZ.localize(dt)
    jal = jdatetime.datetime.fromgregorian(datetime=dt.astimezone(_TZ))
    return jal.strftime("%Y-%m-%dT%H:%M:%S")


class RescheduleTasksProcess:
    """
    Automated process to reschedule remaining tasks.
    Moves incomplete tasks from previous days to the current day.
    """
    
    PROCESS_NAME = "reschedule_remaining_tasks"
    
    @staticmethod
    def execute(db: Session, process_id: str) -> Dict[str, Any]:
        """
        Execute the reschedule process
        
        Args:
            db: Database session
            process_id: Process UUID (for tracking)
            
        Returns:
            Dictionary with execution results
        """
        execution_id = None
        
        try:
            # Create execution record
            execution = AutomatedProcessService.create_execution(
                db=db,
                process_id=process_id,
                status=ProcessStatusEnum.RUNNING
            )
            execution_id = execution.execution_id
            
            logger.info("Starting reschedule remaining tasks process")
            
            # Get current date/time in configured timezone
            now = datetime.now(_TZ)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Find all incomplete tasks with due dates before today
            tasks_to_reschedule = db.query(TaskModel).filter(
                TaskModel.status.in_([StatusEnum.PENDING, StatusEnum.IN_PROGRESS]),
                TaskModel.due_date_gregorian < today_start
            ).all()
            
            logger.info(f"Found {len(tasks_to_reschedule)} tasks to reschedule")
            
            rescheduled_count = 0
            task_details = []
            
            for task in tasks_to_reschedule:
                try:
                    old_due_date = task.due_date_gregorian
                    
                    # Update to current day, preserving the time if it exists
                    if old_due_date:
                        # Extract time from old due date
                        new_due_date = today_start.replace(
                            hour=old_due_date.hour,
                            minute=old_due_date.minute,
                            second=old_due_date.second
                        )
                    else:
                        # If no due date, set to end of today
                        new_due_date = today_start.replace(hour=23, minute=59, second=59)
                    
                    # Update Gregorian date
                    task.due_date_gregorian = new_due_date
                    
                    # Update Jalali date
                    task.due_date_jalali = _to_jalali_iso(new_due_date)
                    
                    rescheduled_count += 1
                    
                    task_details.append({
                        "task_id": str(task.task_id),
                        "task_name": task.name,
                        "user_id": str(task.user_id),
                        "old_due_date": old_due_date.isoformat() if old_due_date else None,
                        "new_due_date": new_due_date.isoformat()
                    })
                    
                    logger.debug(f"Rescheduled task {task.task_id}: {task.name}")
                    
                except Exception as e:
                    logger.error(f"Error rescheduling task {task.task_id}: {e}")
                    continue
            
            # Commit all changes
            db.commit()
            
            # Update last executed timestamp
            AutomatedProcessService.update_last_executed(db, process_id)
            
            result = {
                "success": True,
                "tasks_found": len(tasks_to_reschedule),
                "tasks_rescheduled": rescheduled_count,
                "execution_time": now.isoformat(),
                "task_details": task_details[:100]  # Limit to first 100 for storage
            }
            
            # Update execution record
            if execution_id:
                AutomatedProcessService.update_execution(
                    db=db,
                    execution_id=execution_id,
                    status=ProcessStatusEnum.COMPLETED,
                    result=result
                )
            
            logger.info(f"Reschedule process completed: {rescheduled_count} tasks rescheduled")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in reschedule process: {e}")
            
            # Update execution record with error
            if execution_id:
                try:
                    AutomatedProcessService.update_execution(
                        db=db,
                        execution_id=execution_id,
                        status=ProcessStatusEnum.FAILED,
                        error_message=str(e)
                    )
                except Exception as update_error:
                    logger.error(f"Error updating execution record: {update_error}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": datetime.now(_TZ).isoformat()
            }


# Registry of all automated processes
AUTOMATED_PROCESSES = {
    RescheduleTasksProcess.PROCESS_NAME: RescheduleTasksProcess
}


def get_process_executor(process_name: str):
    """
    Get the executor class for a process by name
    
    Args:
        process_name: Name of the process
        
    Returns:
        Process executor class or None if not found
    """
    return AUTOMATED_PROCESSES.get(process_name)
