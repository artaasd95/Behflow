"""
Task management tools for the Behflow agent - Database Integrated Version
These tools are used by the LangGraph agent to manage tasks via PostgreSQL database
"""
from typing import List, Optional
from uuid import UUID
from langchain_core.tools import tool
from datetime import datetime, timezone
from contextlib import contextmanager

from behflow_agent.models import Task
from app.database.task_service import TaskService
from app.database.database import SessionLocal
from app.database.models import PriorityEnum, StatusEnum
from shared.logger import get_logger

logger = get_logger(__name__)

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


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _task_model_to_string(task) -> str:
    """Convert a TaskModel to a formatted string."""
    due_info = ""
    if task.due_date_gregorian:
        due_info = f", Due: {task.due_date_gregorian.strftime('%Y-%m-%d')}"
    tags_info = f", Tags: {', '.join(task.tags)}" if task.tags else ""
    return f"[{task.status.value}] {task.name} (Priority: {task.priority.value}, ID: {task.task_id}{due_info}{tags_info})"


@tool
def add_task(
    name: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
) -> str:
    """Add a new task for the current agent user (user is set by the agent instance).

    The agent must set the current user context (UUID string) before invoking tools.

    Args:
        name: Task name (required)
        description: Task description (optional)
        priority: Priority level - 'high', 'medium', or 'low' (default: 'medium')
        tags: List of tags (optional)
        due_date: Due date in format 'YYYY-MM-DD' (optional)

    Returns a success message with the created task ID, or an error message.
    """
    try:
        uid = _require_user()
        logger.info("Adding task for user=%s name=%s priority=%s", uid, name, priority)
        
        # Parse due date if provided
        due_date_gregorian = None
        if due_date:
            try:
                due_date_gregorian = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return f"Error: Invalid date format. Use YYYY-MM-DD"
        
        # Create Task pydantic model
        task = Task(
            user_id=uid,
            name=name,
            description=description,
            priority=priority,
            tags=tags,
            due_date_gregorian=due_date_gregorian,
        )
        
        # Save to database
        with get_db_session() as db:
            db_task = TaskService.create_task(db, task)
            logger.info("Task created in DB: %s for user=%s", db_task.task_id, uid)
            return f"Task '{name}' created successfully with ID: {db_task.task_id}"
            
    except Exception as e:
        logger.exception("Error creating task: %s", e)
        return f"Error creating task: {str(e)}"


@tool
def remove_task(task_id: str) -> str:
    """Remove a task by ID (only allowed for current user).
    
    Args:
        task_id: The UUID of the task to remove
        
    Returns:
        Success or error message
    """
    try:
        uid = _require_user()
        logger.info("User %s attempting to remove task %s", uid, task_id)
        tid = UUID(task_id)
        
        with get_db_session() as db:
            # Get the task first to verify ownership
            task = TaskService.get_task_by_id(db, tid)
            
            if not task:
                logger.warning("Attempted to remove non-existent task %s by user %s", task_id, uid)
                return f"Task {task_id} not found"
                
            if task.user_id != uid:
                logger.warning("User %s attempted to remove task %s which they do not own", uid, task_id)
                return f"Task {task_id} does not belong to the current user"
            
            # Delete the task
            success = TaskService.delete_task(db, tid)
            
            if success:
                logger.info("Task %s removed by user %s", task_id, uid)
                return f"Task '{task.name}' (ID: {task_id}) removed successfully"
            else:
                return f"Failed to remove task {task_id}"
                
    except Exception as e:
        logger.exception("Error removing task: %s", e)
        return f"Error removing task: {str(e)}"


@tool
def update_task(
    task_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Update a task's properties (only allowed for current user).
    
    Args:
        task_id: The UUID of the task to update
        name: New task name (optional)
        description: New description (optional)
        priority: New priority - 'high', 'medium', or 'low' (optional)
        status: New status - 'pending', 'in_progress', 'completed', 'cancelled' (optional)
        tags: New tags list (optional)
        
    Returns:
        Success or error message
    """
    try:
        uid = _require_user()
        logger.info("User %s updating task %s", uid, task_id)
        tid = UUID(task_id)
        
        with get_db_session() as db:
            # Verify task exists and belongs to user
            task = TaskService.get_task_by_id(db, tid)
            
            if not task:
                return f"Task {task_id} not found"
                
            if task.user_id != uid:
                return f"Task {task_id} does not belong to the current user"
            
            # Convert priority and status to enums if provided
            priority_enum = PriorityEnum[priority.upper()] if priority else None
            status_enum = StatusEnum[status.upper()] if status else None
            
            # Update the task
            updated_task = TaskService.update_task(
                db=db,
                task_id=tid,
                name=name,
                description=description,
                priority=priority_enum,
                status=status_enum,
                tags=tags
            )
            
            if updated_task:
                logger.info("Task %s updated by user %s", task_id, uid)
                changes = []
                if name: changes.append(f"name to '{name}'")
                if description: changes.append("description")
                if priority: changes.append(f"priority to '{priority}'")
                if status: changes.append(f"status to '{status}'")
                if tags: changes.append("tags")
                
                changes_str = ", ".join(changes) if changes else "properties"
                return f"Task '{updated_task.name}' updated successfully ({changes_str})"
            else:
                return f"Failed to update task {task_id}"
                
    except Exception as e:
        logger.exception("Error updating task: %s", e)
        return f"Error updating task: {str(e)}"


@tool
def change_task_priority(task_id: str, priority: str) -> str:
    """Change the priority of a task (only allowed for current user).
    
    Args:
        task_id: The UUID of the task
        priority: New priority - 'high', 'medium', or 'low'
        
    Returns:
        Success or error message
    """
    return update_task(task_id=task_id, priority=priority)


@tool
def complete_task(task_id: str) -> str:
    """Mark a task as completed (only allowed for current user).
    
    Args:
        task_id: The UUID of the task to complete
        
    Returns:
        Success or error message
    """
    return update_task(task_id=task_id, status="completed")


@tool
def get_all_tasks(status_filter: Optional[str] = None, limit: int = 100) -> str:
    """Get all tasks for the current user.
    
    Args:
        status_filter: Filter by status - 'pending', 'in_progress', 'completed', 'cancelled' (optional)
        limit: Maximum number of tasks to return (default: 100)
        
    Returns:
        Formatted list of tasks
    """
    try:
        uid = _require_user()
        logger.info("Retrieving all tasks for user %s", uid)
        
        # Convert status filter to enum if provided
        status_enum = StatusEnum[status_filter.upper()] if status_filter else None
        
        with get_db_session() as db:
            tasks = TaskService.get_user_tasks(
                db=db,
                user_id=uid,
                status=status_enum,
                limit=limit
            )
            
            if not tasks:
                logger.info("No tasks found for user %s", uid)
                return "No tasks found for current user"

            result = "\n".join([
                f"- {_task_model_to_string(task)}"
                for task in tasks
            ])
            
            logger.debug("Found %d tasks for user %s", len(tasks), uid)
            
            status_info = f" (Status: {status_filter})" if status_filter else ""
            return f"Tasks for current user{status_info}:\n{result}"
            
    except Exception as e:
        logger.exception("Error retrieving tasks: %s", e)
        return f"Error retrieving tasks: {str(e)}"


@tool
def search_tasks(search_term: str) -> str:
    """Search for tasks by name or description using a search term.
    
    Use this tool when the user wants to find specific tasks by keywords,
    such as 'find my task about reading' or 'search for book tasks'.
    
    Args:
        search_term: Keywords to search for in task names and descriptions
        
    Returns:
        Matching tasks or a message if none found
    """
    try:
        uid = _require_user()
        logger.info("Searching tasks for user %s with term: %s", uid, search_term)
        
        with get_db_session() as db:
            tasks = TaskService.search_tasks(
                db=db,
                user_id=uid,
                search_term=search_term
            )
            
            if not tasks:
                return f"No tasks found matching '{search_term}'"
            
            result = "\n".join([
                f"- {_task_model_to_string(task)}"
                + (f"\n  Description: {task.description}" if task.description else "")
                for task in tasks
            ])
            
            logger.info("Found %d matching tasks for user %s", len(tasks), uid)
            return f"Found {len(tasks)} task(s) matching '{search_term}':\n{result}"
            
    except Exception as e:
        logger.exception("Error searching tasks: %s", e)
        return f"Error searching tasks: {str(e)}"


@tool
def get_overdue_tasks() -> str:
    """Get all overdue tasks for the current user.
    
    Returns tasks that have a due date in the past and are not yet completed.
    
    Returns:
        List of overdue tasks
    """
    try:
        uid = _require_user()
        logger.info("Retrieving overdue tasks for user %s", uid)
        
        with get_db_session() as db:
            tasks = TaskService.get_overdue_tasks(db=db, user_id=uid)
            
            if not tasks:
                return "No overdue tasks found. Great job staying on track!"
            
            result = "\n".join([
                f"- {_task_model_to_string(task)}"
                for task in tasks
            ])
            
            logger.info("Found %d overdue tasks for user %s", len(tasks), uid)
            return f"⚠️ You have {len(tasks)} overdue task(s):\n{result}"
            
    except Exception as e:
        logger.exception("Error retrieving overdue tasks: %s", e)
        return f"Error retrieving overdue tasks: {str(e)}"


@tool
def get_task_statistics() -> str:
    """Get task statistics for the current user.
    
    Returns a summary of tasks by status (total, pending, in progress, completed, cancelled).
    
    Returns:
        Formatted task statistics
    """
    try:
        uid = _require_user()
        logger.info("Retrieving task statistics for user %s", uid)
        
        with get_db_session() as db:
            stats = TaskService.get_task_statistics(db=db, user_id=uid)
            
            result = f"""📊 Your Task Statistics:
• Total tasks: {stats['total']}
• Pending: {stats['pending']}
• In Progress: {stats['in_progress']}
• Completed: {stats['completed']}
• Cancelled: {stats['cancelled']}"""
            
            # Calculate completion rate
            if stats['total'] > 0:
                completion_rate = (stats['completed'] / stats['total']) * 100
                result += f"\n• Completion rate: {completion_rate:.1f}%"
            
            logger.info("Task statistics retrieved for user %s", uid)
            return result
            
    except Exception as e:
        logger.exception("Error retrieving task statistics: %s", e)
        return f"Error retrieving task statistics: {str(e)}"


@tool
def get_tasks_by_tag(tag: str) -> str:
    """Get all tasks with a specific tag for the current user.
    
    Args:
        tag: The tag to filter by
        
    Returns:
        List of tasks with the specified tag
    """
    try:
        uid = _require_user()
        logger.info("Retrieving tasks with tag '%s' for user %s", tag, uid)
        
        with get_db_session() as db:
            tasks = TaskService.get_tasks_by_tag(db=db, user_id=uid, tag=tag)
            
            if not tasks:
                return f"No tasks found with tag '{tag}'"
            
            result = "\n".join([
                f"- {_task_model_to_string(task)}"
                for task in tasks
            ])
            
            logger.info("Found %d tasks with tag '%s' for user %s", len(tasks), tag, uid)
            return f"Tasks with tag '{tag}' ({len(tasks)}):\n{result}"
            
    except Exception as e:
        logger.exception("Error retrieving tasks by tag: %s", e)
        return f"Error retrieving tasks by tag: {str(e)}"


@tool
def group_tasks_by_priority() -> str:
    """Group all tasks by priority for the current user."""
    try:
        uid = _require_user()
        logger.info("Grouping tasks by priority for user %s", uid)
        
        with get_db_session() as db:
            tasks = TaskService.get_user_tasks(db=db, user_id=uid, limit=1000)
            
            grouped = {"high": [], "medium": [], "low": []}
            for task in tasks:
                grouped[task.priority.value].append(task)

            result = []
            for priority in ["high", "medium", "low"]:
                tasks_list = grouped[priority]
                if tasks_list:
                    result.append(f"\n{priority.upper()} Priority ({len(tasks_list)}):")
                    result.extend([f"  - {task.name} (ID: {task.task_id})" for task in tasks_list])

            return "\n".join(result) if result else "No tasks found for current user"
            
    except Exception as e:
        logger.exception("Error grouping tasks by priority: %s", e)
        return f"Error grouping tasks: {str(e)}"


@tool
def group_tasks_by_status() -> str:
    """Group all tasks by status for the current user."""
    try:
        uid = _require_user()
        logger.info("Grouping tasks by status for user %s", uid)
        
        with get_db_session() as db:
            tasks = TaskService.get_user_tasks(db=db, user_id=uid, limit=1000)
            
            from collections import defaultdict
            grouped = defaultdict(list)
            for task in tasks:
                grouped[task.status.value].append(task)

            result = []
            for status in ["pending", "in_progress", "completed", "cancelled"]:
                tasks_list = grouped.get(status, [])
                if tasks_list:
                    result.append(f"\n{status.upper().replace('_', ' ')} ({len(tasks_list)}):")
                    result.extend([f"  - {task.name} (ID: {task.task_id})" for task in tasks_list])

            return "\n".join(result) if result else "No tasks found for current user"
            
    except Exception as e:
        logger.exception("Error grouping tasks by status: %s", e)
        return f"Error grouping tasks by status: {str(e)}"




# Export all tools as a list for easy binding
TASK_TOOLS = [
    add_task,
    remove_task,
    update_task,
    change_task_priority,
    complete_task,
    get_all_tasks,
    search_tasks,
    get_overdue_tasks,
    get_task_statistics,
    get_tasks_by_tag,
    group_tasks_by_priority,
    group_tasks_by_status,
]

