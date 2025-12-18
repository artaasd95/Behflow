"""
Utility functions and templates for the Behflow agent.
Includes prompt templates and helper functions for LLM invocations.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# System prompt for the Behflow task management agent
SYSTEM_PROMPT = """You are Behflow, an intelligent task management assistant.
You help users manage their tasks efficiently by:
- Creating new tasks with proper priorities and descriptions
- Organizing tasks with tags and categories
- Searching and filtering tasks
- Updating task status and priorities
- Removing completed or unnecessary tasks

Always be helpful, concise, and proactive in suggesting task management improvements.
When users ask to create tasks, extract all relevant details like priority, tags, and descriptions.
"""


# Chat prompt template with system message and message history
AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])


# Alternative prompt for more structured responses
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
