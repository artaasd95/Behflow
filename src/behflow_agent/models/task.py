"""
Task model for Behflow agent
Stores dates in both Gregorian and Jalali formats; times are optional.
Timezone is read from BEHFLOW_TIMEZONE env var (defaults to Asia/Tehran).
"""
from __future__ import annotations
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import os

import pytz
import jdatetime
from pydantic import BaseModel, Field, field_validator

# Timezone configuration
_TIMEZONE = os.getenv("BEHFLOW_TIMEZONE", "Asia/Tehran")
_TZ = pytz.timezone(_TIMEZONE)


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def _to_jalali_iso(dt: datetime) -> str:
    """Convert a timezone-aware Gregorian datetime to a Jalali ISO string."""
    # Ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = _TZ.localize(dt)
    jal = jdatetime.datetime.fromgregorian(datetime=dt.astimezone(_TZ))
    # Use ISO-like format YYYY-MM-DDTHH:MM:SS
    return jal.strftime("%Y-%m-%dT%H:%M:%S")


class Task(BaseModel):
    """Task model.

    Fields:
      - task_id: UUID (generated if not provided)
      - user_id: UUID (maps to a user UUID managed elsewhere)
      - name: str
      - description: Optional[str]
      - due_date_gregorian: Optional[datetime]
      - due_date_jalali: Optional[str]
      - date_added_gregorian: datetime (auto-set to now in service timezone)
      - date_added_jalali: str (auto-generated from `date_added_gregorian`)
      - priority: Priority enum
      - tags: Optional[list[str]]
      - status: Status enum
    """

    task_id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    name: str
    description: Optional[str] = None

    due_date_gregorian: Optional[datetime] = None
    due_date_jalali: Optional[str] = None

    date_added_gregorian: datetime = Field(default_factory=lambda: datetime.now(_TZ))
    date_added_jalali: str = Field(default_factory=lambda: _to_jalali_iso(datetime.now(_TZ)))

    priority: Priority = Priority.MEDIUM
    tags: Optional[List[str]] = None
    status: Status = Status.PENDING

    @field_validator("due_date_gregorian", mode="before")
    def _ensure_due_gregorian_tz(cls, v):
        if v is None:
            return v
        if v.tzinfo is None:
            return _TZ.localize(v)
        return v.astimezone(_TZ)

    @field_validator("date_added_gregorian", mode="before")
    def _ensure_date_added_tz(cls, v):
        if v is None:
            return datetime.now(_TZ)
        if v.tzinfo is None:
            return _TZ.localize(v)
        return v.astimezone(_TZ)

    @field_validator("due_date_jalali", mode="after")
    def _sync_due_jalali(cls, v, info):
        # If jalali provided, trust it; otherwise compute from gregorian
        if v:
            return v
        gd = info.data.get("due_date_gregorian")
        if gd:
            return _to_jalali_iso(gd)
        return None

    @field_validator("date_added_jalali", mode="after")
    def _sync_date_added_jalali(cls, v, info):
        # Compute from date_added_gregorian
        gad = info.data.get("date_added_gregorian")
        if gad:
            return _to_jalali_iso(gad)
        return v

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
