# Automated Processes System

This document describes the automated processes system in Behflow, which allows for scheduled and manual execution of recurring tasks.

## Overview

The automated processes system provides:
- **Time-based triggers**: Execute processes on a schedule (cron-like)
- **Manual triggers**: Execute processes on demand
- **Event-based triggers**: Execute processes in response to events (future enhancement)
- **Execution tracking**: Monitor process runs and results
- **Configurable scheduling**: Customize execution times via environment variables

## Architecture

### Components

1. **Models** (`behflow_agent/models/automated_process.py`)
   - `AutomatedProcessBase`: Base model for all automated processes
   - `RescheduleTasksProcess`: Specific implementation for task rescheduling
   - `TriggerType`: Enum for trigger types (manual, time_based, event_based)
   - `ProcessStatus`: Enum for execution status

2. **Database Models** (`backend/app/database/models.py`)
   - `AutomatedProcessModel`: Stores process configurations
   - `AutomatedProcessExecutionModel`: Tracks execution history

3. **Services** (`backend/app/database/automated_process_service.py`)
   - CRUD operations for automated processes
   - Execution tracking and history

4. **Process Implementations** (`backend/app/database/automated_processes.py`)
   - Actual business logic for each process
   - Registry of available processes

5. **Scheduler** (`backend/app/scheduler.py`)
   - APScheduler integration
   - Job scheduling and management
   - Lifecycle management (start/stop/reload)

## Current Automated Processes

### 1. Reschedule Remaining Tasks

**Purpose**: Automatically moves incomplete tasks from previous days to the current day.

**Trigger**: Time-based (daily)

**Default Schedule**: 7:30 AM (configurable)

**Configuration**:
```bash
# In .env file
RESCHEDULE_HOUR=7
RESCHEDULE_MINUTE=30
BEHFLOW_TIMEZONE=Asia/Tehran
```

**Behavior**:
- Finds all tasks with status `pending` or `in_progress`
- Filters tasks with due dates before today
- Updates their due date to today, preserving the original time
- Logs all rescheduled tasks for auditing

**Execution Results**:
```json
{
  "success": true,
  "tasks_found": 15,
  "tasks_rescheduled": 15,
  "execution_time": "2025-12-18T07:30:00+03:30",
  "task_details": [...]
}
```

## Setup

### 1. Database Migration

Run the migration script to create the required tables:

```bash
psql -U your_user -d behflow -f infra/migrations/001_add_automated_processes.sql
```

Or if using SQLAlchemy, the tables will be created automatically on first run.

### 2. Install Dependencies

```bash
pip install -r src/backend/requirements.txt
```

This includes APScheduler for job scheduling.

### 3. Configure Environment

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
BEHFLOW_TIMEZONE=Asia/Tehran
RESCHEDULE_HOUR=7
RESCHEDULE_MINUTE=30
```

### 4. Run the Application

The scheduler starts automatically with the FastAPI application:

```bash
cd src/backend
uvicorn app.main:app --reload
```

## Usage

### Viewing Scheduled Jobs

The scheduler logs all scheduled jobs on startup:

```
INFO:     Automated process scheduler started
INFO:     Scheduled jobs: 1
INFO:       - reschedule_remaining_tasks: next run at 2025-12-19 07:30:00+03:30
```

### Manual Execution

To manually trigger a process (future enhancement - API endpoint):

```python
from app.database.automated_processes import RescheduleTasksProcess
from app.database.database import get_db

db = next(get_db())
result = RescheduleTasksProcess.execute(db, process_id)
```

### Checking Execution History

Query the `automated_process_executions` table:

```sql
SELECT 
    execution_id,
    status,
    started_at,
    completed_at,
    result->>'tasks_rescheduled' as tasks_rescheduled
FROM automated_process_executions
WHERE process_id = (
    SELECT process_id 
    FROM automated_processes 
    WHERE name = 'reschedule_remaining_tasks'
)
ORDER BY started_at DESC
LIMIT 10;
```

## Adding New Automated Processes

### 1. Define the Process Model

In `behflow_agent/models/automated_process.py`:

```python
class MyCustomProcess(AutomatedProcessBase):
    name: str = "my_custom_process"
    description: str = "Description of what it does"
    trigger_type: TriggerType = TriggerType.TIME_BASED
    
    def __init__(self, **data):
        if "schedule_config" not in data:
            data["schedule_config"] = {
                "hour": 9,
                "minute": 0,
                "timezone": _TIMEZONE
            }
        super().__init__(**data)
```

### 2. Implement the Process Logic

In `backend/app/database/automated_processes.py`:

```python
class MyCustomProcess:
    PROCESS_NAME = "my_custom_process"
    
    @staticmethod
    def execute(db: Session, process_id: str) -> Dict[str, Any]:
        execution_id = None
        
        try:
            # Create execution record
            execution = AutomatedProcessService.create_execution(
                db=db,
                process_id=process_id,
                status=ProcessStatusEnum.RUNNING
            )
            execution_id = execution.execution_id
            
            # Your business logic here
            # ...
            
            result = {
                "success": True,
                # ... your results
            }
            
            # Update execution record
            AutomatedProcessService.update_execution(
                db=db,
                execution_id=execution_id,
                status=ProcessStatusEnum.COMPLETED,
                result=result
            )
            
            return result
            
        except Exception as e:
            if execution_id:
                AutomatedProcessService.update_execution(
                    db=db,
                    execution_id=execution_id,
                    status=ProcessStatusEnum.FAILED,
                    error_message=str(e)
                )
            return {"success": False, "error": str(e)}

# Register the process
AUTOMATED_PROCESSES["my_custom_process"] = MyCustomProcess
```

### 3. Initialize in Database

In `backend/app/database/init_automated_processes.py`, add:

```python
# Create your custom process
AutomatedProcessService.create_process(
    db=db,
    name="my_custom_process",
    description="Description",
    trigger_type=TriggerTypeEnum.TIME_BASED,
    schedule_config={"hour": 9, "minute": 0, "timezone": _TIMEZONE},
    process_config={},
    is_enabled=True
)
```

### 4. Restart the Application

The scheduler will automatically pick up the new process.

## Troubleshooting

### Process Not Running

1. Check if the process is enabled:
   ```sql
   SELECT name, is_enabled FROM automated_processes;
   ```

2. Check scheduler logs:
   ```
   grep "scheduler" app.log
   ```

3. Verify schedule configuration:
   ```sql
   SELECT name, schedule_config FROM automated_processes;
   ```

### Execution Failures

Check the execution history for error messages:

```sql
SELECT 
    execution_id,
    status,
    error_message,
    started_at
FROM automated_process_executions
WHERE status = 'failed'
ORDER BY started_at DESC;
```

### Reloading Schedules

If you update a process configuration, reload the schedules:

```python
from app.scheduler import reload_schedules
reload_schedules()
```

## Future Enhancements

- [ ] API endpoints for manual process execution
- [ ] API endpoints for process management (CRUD)
- [ ] Web UI for monitoring execution history
- [ ] Event-based triggers
- [ ] Process dependencies and chaining
- [ ] Retry logic for failed executions
- [ ] Notification system for failures
- [ ] Process execution timeouts
- [ ] Concurrent execution limits

## Technical Details

### Timezone Handling

All times are stored in UTC in the database but scheduled according to the configured timezone (`BEHFLOW_TIMEZONE`). This ensures correct execution across different server locations.

### Concurrency

Each process is configured with `max_instances=1` to prevent concurrent execution. If a process is still running when the next scheduled time arrives, the new execution will be skipped.

### Error Handling

All process executions are wrapped in try-except blocks. Errors are:
1. Logged to the application logs
2. Stored in the execution record
3. Not propagated to the scheduler (scheduler continues running)

### Database Transactions

Each process execution uses a separate database session to ensure proper transaction isolation and cleanup.
