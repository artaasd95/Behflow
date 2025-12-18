"""
Automated Process Models for Behflow
Defines base models for scheduled and manual automated processes
"""
from __future__ import annotations
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import os

import pytz
from pydantic import BaseModel, Field

# Timezone configuration
_TIMEZONE = os.getenv("BEHFLOW_TIMEZONE", "Asia/Tehran")
_TZ = pytz.timezone(_TIMEZONE)


class TriggerType(str, Enum):
    """Type of trigger for automated process"""
    MANUAL = "manual"
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"


class ProcessStatus(str, Enum):
    """Status of automated process execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


class AutomatedProcessBase(BaseModel):
    """Base model for automated processes"""
    
    process_id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    
    # For time-based triggers (cron-like schedule)
    schedule_config: Optional[Dict[str, Any]] = None  # e.g., {"hour": 7, "minute": 30}
    
    # Process configuration/parameters
    process_config: Optional[Dict[str, Any]] = None
    
    is_enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(_TZ))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(_TZ))
    
    class Config:
        use_enum_values = True


class AutomatedProcessExecution(BaseModel):
    """Model for tracking automated process executions"""
    
    execution_id: UUID = Field(default_factory=uuid4)
    process_id: UUID
    status: ProcessStatus = ProcessStatus.PENDING
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution results
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True


class RescheduleTasksProcess(AutomatedProcessBase):
    """
    Specific process for rescheduling remaining tasks.
    Moves incomplete tasks from previous day(s) to current day.
    """
    
    name: str = "Reschedule Remaining Tasks"
    description: str = "Reschedules incomplete tasks from previous days to today"
    trigger_type: TriggerType = TriggerType.TIME_BASED
    
    def __init__(self, **data):
        # Set default schedule if not provided
        if "schedule_config" not in data or data["schedule_config"] is None:
            # Default to 7:30 AM, but can be overridden by env vars
            default_hour = int(os.getenv("RESCHEDULE_HOUR", "7"))
            default_minute = int(os.getenv("RESCHEDULE_MINUTE", "30"))
            data["schedule_config"] = {
                "hour": default_hour,
                "minute": default_minute,
                "timezone": _TIMEZONE
            }
        
        if "process_config" not in data:
            data["process_config"] = {
                "include_statuses": ["pending", "in_progress"],
                "update_to_today": True
            }
        
        super().__init__(**data)
