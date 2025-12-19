"""
Utility functions and templates for the Behflow agent.
Includes prompt templates and helper functions for LLM invocations.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
import os
import pytz
import jdatetime


# Timezone configuration
_TIMEZONE = os.getenv("BEHFLOW_TIMEZONE", "Asia/Tehran")
_TZ = pytz.timezone(_TIMEZONE)


def get_current_time_context() -> str:
    """
    Get current time in both Gregorian and Jalali formats.
    
    Returns:
        Formatted string with current date and time
    """
    now = datetime.now(_TZ)
    
    # Gregorian format
    gregorian_str = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Jalali format
    jal = jdatetime.datetime.fromgregorian(datetime=now)
    jalali_str = jal.strftime("%Y-%m-%d %H:%M:%S")
    
    return f"Current time: {gregorian_str} (Gregorian) | {jalali_str} (Jalali/Shamsi)"


# System prompt for the Behflow task management agent
def get_system_prompt() -> str:
    """Get system prompt with current time context"""
    time_context = get_current_time_context()
    
    return f"""You are Behflow, an intelligent task management assistant.

{time_context}

You help users manage their tasks efficiently by:
- Creating new tasks with proper priorities, descriptions, tags, and due dates
- Organizing tasks with tags and categories
- Searching and filtering tasks by keywords, status, priority, or tags
- Finding specific tasks based on descriptions or content
- Updating task properties (name, description, priority, status, tags)
- Completing or removing tasks
- Tracking overdue tasks and providing reminders
- Providing task statistics and insights

When creating tasks with dates, use the current time as reference.
Always be helpful, concise, and proactive in suggesting task management improvements.
When users ask to create tasks, extract all relevant details like priority, tags, due dates, and descriptions.

IMPORTANT - When users want to find, remove, or modify a specific task:
1. First use search_tasks() with relevant keywords from their request
2. If multiple matches, ask user which one they meant
3. Then perform the requested action with the correct task ID

Examples:
- "remove the task about reading" -> search_tasks("reading") then remove_task(task_id)
- "find my book tasks" -> search_tasks("book")
- "what tasks do I have for today" -> get_all_tasks() and filter by date
- "mark reading task as done" -> search_tasks("reading") then complete_task(task_id)
- "show my overdue tasks" -> get_overdue_tasks()
- "how many tasks do I have" -> get_task_statistics()
- "change priority of coding task" -> search_tasks("coding") then update_task(task_id, priority="high")

Available tools include:
- add_task: Create new tasks
- search_tasks: Find tasks by keywords
- get_all_tasks: List all tasks (optionally filter by status)
- get_overdue_tasks: Show tasks past their due date
- get_task_statistics: Get overview of task counts
- get_tasks_by_tag: Filter tasks by specific tag
- update_task: Modify task properties
- complete_task: Mark task as completed
- remove_task: Delete a task
- group_tasks_by_priority: Organize by priority level
- group_tasks_by_status: Organize by status
"""


# NOTE: create the prompt dynamically per-request so the current time is fresh

def get_agent_prompt() -> ChatPromptTemplate:
    """Return a prompt template with the current system prompt (dynamic)."""
    return ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        MessagesPlaceholder(variable_name="messages"),
    ])


# Alternative prompt for more structured responses (keeps using a passed-in system_prompt)
STRUCTURED_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="messages"),
])


def create_custom_prompt(system_message: str) -> ChatPromptTemplate:
    """
    Create a custom prompt template with a specific system message.
    
    Args:
        system_message: The system message to use
        
    Returns:
        ChatPromptTemplate configured with the custom system message
    """
    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="messages"),
    ])


def format_task_context(tasks: list[dict]) -> str:
    """
    Format a list of tasks for inclusion in the context.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        Formatted string representation of tasks
    """
    if not tasks:
        return "No tasks found."
    
    formatted = []
    for task in tasks:
        task_str = f"- {task.get('name', 'Unnamed')} (Priority: {task.get('priority', 'medium')})"
        if task.get('description'):
            task_str += f"\n  Description: {task['description']}"
        if task.get('tags'):
            task_str += f"\n  Tags: {', '.join(task['tags'])}"
        formatted.append(task_str)
    
    return "\n".join(formatted)
