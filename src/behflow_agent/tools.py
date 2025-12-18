"""
Task management tools for the Behflow agent
These tools are used by the LangGraph agent to manage tasks
"""
from typing import List, Optional
from uuid import UUID
from langchain_core.tools import tool
from behflow_agent.models import Task
from shared.logger import get_logger

logger = get_logger(__name__)

# In-memory storage for demonstration (replace with DB later)
_TASK_STORE: dict[UUID, Task] = {}

# Current user context (set by the agent when invoking tools)
_CURRENT_USER_ID: str | None = None


def set_current_user(user_uuid: str) -> None:
    """Set the current user UUID (string) for the tool invocation context."""
    global _CURRENT_USER_ID
    _CURRENT_USER_ID = user_uuid
    logger.debug("Set current user to %s", user_uuid)


def clear_current_user() -> None:
    """Clear the current user context."""
    global _CURRENT_USER_ID
    logger.debug("Clearing current user (was: %s)", _CURRENT_USER_ID)
    _CURRENT_USER_ID = None


def _require_user() -> UUID:
    """Return the current user UUID or raise a ValueError if not set."""
    if not _CURRENT_USER_ID:
        logger.warning("Operation attempted without a current user set")
        raise ValueError("No current user set in agent context")
    return UUID(_CURRENT_USER_ID)


@tool
def add_task(
    name: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
) -> str:
    """Add a new task for the current agent user (user is set by the agent instance).

    The agent must set the current user context (UUID string) before invoking tools.

    Returns a success message with the created task ID, or an error message.
    """
    try:
        uid = _require_user()
        logger.info("Adding task for user=%s name=%s priority=%s", uid, name, priority)
        task = Task(
            user_id=uid,
            name=name,
            description=description,
            priority=priority,
            tags=tags,
        )
        _TASK_STORE[task.task_id] = task
        logger.info("Task created: %s for user=%s", task.task_id, uid)
        return f"Task created successfully with ID: {task.task_id}"
    except Exception as e:
        logger.exception("Error creating task: %s", e)
        return f"Error creating task: {str(e)}"


@tool
def remove_task(task_id: str) -> str:
    """Remove a task by ID (only allowed for current user)."""
    try:
        uid = _require_user()
        logger.info("User %s attempting to remove task %s", uid, task_id)
        tid = UUID(task_id)
        task = _TASK_STORE.get(tid)
        if not task:
            logger.warning("Attempted to remove non-existent task %s by user %s", task_id, uid)
            return f"Task {task_id} not found"
        if task.user_id != uid:
            logger.warning("User %s attempted to remove task %s which they do not own", uid, task_id)
            return f"Task {task_id} does not belong to the current user"
        del _TASK_STORE[tid]
        logger.info("Task %s removed by user %s", task_id, uid)
        return f"Task {task_id} removed successfully"
    except Exception as e:
        logger.exception("Error removing task: %s", e)
        return f"Error removing task: {str(e)}"


@tool
def change_task_priority(task_id: str, priority: str) -> str:
    """Change the priority of a task (only allowed for current user)."""
    try:
        uid = _require_user()
        logger.info("User %s changing priority for task %s to %s", uid, task_id, priority)
        tid = UUID(task_id)
        task = _TASK_STORE.get(tid)
        if not task:
            logger.warning("Task %s not found when user %s attempted priority change", task_id, uid)
            return f"Task {task_id} not found"
        if task.user_id != uid:
            logger.warning("User %s attempted to change priority for task %s which they do not own", uid, task_id)
            return f"Task {task_id} does not belong to the current user"
        task.priority = priority
        logger.info("Task %s priority updated to %s by user %s", task_id, priority, uid)
        return f"Task {task_id} priority updated to {priority}"
    except Exception as e:
        logger.exception("Error updating priority: %s", e)
        return f"Error updating priority: {str(e)}"


@tool
def get_all_tasks() -> str:
    """Get all tasks for the current user."""
    try:
        uid = _require_user()
        logger.info("Retrieving all tasks for user %s", uid)
        user_tasks = [task for task in _TASK_STORE.values() if task.user_id == uid]
        if not user_tasks:
            logger.info("No tasks found for user %s", uid)
            return "No tasks found for current user"

        result = "\n".join([
            f"- [{task.status}] {task.name} (Priority: {task.priority}, ID: {task.task_id})"
            for task in user_tasks
        ])
        logger.debug("Found %d tasks for user %s", len(user_tasks), uid)
        return f"Tasks for current user:\n{result}"
    except Exception as e:
        logger.exception("Error retrieving tasks: %s", e)
        return f"Error retrieving tasks: {str(e)}"


@tool
def group_tasks_by_priority() -> str:
    """Group all tasks by priority for the current user."""
    try:
        uid = _require_user()
        logger.info("Grouping tasks by priority for user %s", uid)
        user_tasks = [task for task in _TASK_STORE.values() if task.user_id == uid]

        grouped = {"high": [], "medium": [], "low": []}
        for task in user_tasks:
            grouped[task.priority].append(task)

        result = []
        for priority in ["high", "medium", "low"]:
            tasks = grouped[priority]
            if tasks:
                result.append(f"\n{priority.upper()} Priority ({len(tasks)}):")
                result.extend([f"  - {task.name}" for task in tasks])

        return "\n".join(result) if result else "No tasks found for current user"
    except Exception as e:
        logger.exception("Error grouping tasks by priority: %s", e)
        return f"Error grouping tasks: {str(e)}"


@tool
def group_tasks_by_date_created() -> str:
    """Group all tasks by date created for the current user."""
    try:
        uid = _require_user()
        logger.info("Grouping tasks by date created for user %s", uid)
        user_tasks = [task for task in _TASK_STORE.values() if task.user_id == uid]

        # Group by date (without time)
        from collections import defaultdict
        grouped = defaultdict(list)
        for task in user_tasks:
            date_key = task.date_added_gregorian.date()
            grouped[date_key].append(task)

        result = []
        for date in sorted(grouped.keys(), reverse=True):
            tasks = grouped[date]
            result.append(f"\n{date} ({len(tasks)} tasks):")
            result.extend([f"  - {task.name}" for task in tasks])

        return "\n".join(result) if result else "No tasks found for current user"
    except Exception as e:
        logger.exception("Error grouping tasks by date: %s", e)
        return f"Error grouping by date: {str(e)}"


@tool
def group_tasks_by_due_date() -> str:
    """Group all tasks by due date for the current user."""
    try:
        uid = _require_user()
        logger.info("Grouping tasks by due date for user %s", uid)
        user_tasks = [task for task in _TASK_STORE.values() if task.user_id == uid]

        from collections import defaultdict
        grouped = defaultdict(list)
        no_due_date = []

        for task in user_tasks:
            if task.due_date_gregorian:
                date_key = task.due_date_gregorian.date()
                grouped[date_key].append(task)
            else:
                no_due_date.append(task)

        result = []
        for date in sorted(grouped.keys()):
            tasks = grouped[date]
            result.append(f"\nDue {date} ({len(tasks)} tasks):")
            result.extend([f"  - {task.name}" for task in tasks])

        if no_due_date:
            result.append(f"\nNo due date ({len(no_due_date)} tasks):")
            result.extend([f"  - {task.name}" for task in no_due_date])

        return "\n".join(result) if result else "No tasks found for current user"
    except Exception as e:
        logger.exception("Error grouping tasks by due date: %s", e)
        return f"Error grouping tasks by due date: {str(e)}"


# Export all tools as a list for easy binding
TASK_TOOLS = [
    add_task,
    remove_task,
    change_task_priority,
    get_all_tasks,
    group_tasks_by_priority,
    group_tasks_by_date_created,
    group_tasks_by_due_date,
]
