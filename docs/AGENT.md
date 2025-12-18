# Agent System Documentation

## Overview

The Behflow Agent is an AI-powered conversational system built on LangGraph. It orchestrates intelligent task management through natural language interactions, automated processes, and context-aware decision-making.

## Architecture

### Core Components

```
behflow_agent/
├── agent.py              # Main LangGraph agent orchestrator
├── builder.py            # Agent factory and configuration
├── tools.py              # Task management tools
├── llm_config.py         # LLM provider configuration
├── users.py              # User context management
├── utils.py              # Utility functions
├── models/               # Data models
│   ├── task.py          # Task domain model
│   ├── automated_process.py  # Process models
│   └── models.py        # Agent state and shared models
└── nodes/                # Graph processing nodes
    └── graph_nodes.py   # Node implementations
```

### Technology Stack

- **LangGraph**: State machine and graph orchestration
- **LangChain**: Tool integration and LLM abstraction
- **OpenAI/Anthropic**: LLM providers
- **Pydantic**: Data validation and modeling

## Agent State Machine

### State Definition

```python
class AgentState(TypedDict):
    """State passed through the agent graph"""
    messages: List[BaseMessage]      # Conversation history
    user_id: str                     # Current user UUID
    session_id: str                  # Session identifier
    current_task: Optional[Task]     # Active task context
    pending_actions: List[str]       # Queued actions
    metadata: Dict[str, Any]         # Additional context
```

### State Flow

```
User Input → Parse Intent → Execute Tools → Generate Response → Update State
     ↓            ↓              ↓               ↓                ↓
  [Entry]    [Decision]      [Action]      [Response]       [Memory]
```

## Graph Nodes

### 1. Entry Node

**Purpose**: Initialize conversation and validate user context

```python
def entry_node(state: AgentState) -> AgentState:
    """
    Entry point for agent invocation
    - Validate user session
    - Load user context
    - Initialize conversation memory
    """
    user_id = state.get("user_id")
    if not user_id:
        raise ValueError("User ID required")
    
    # Load user context
    user_context = load_user_context(user_id)
    
    # Initialize state
    state["metadata"]["user_context"] = user_context
    state["pending_actions"] = []
    
    return state
```

### 2. Intent Classification Node

**Purpose**: Understand user intent from natural language

```python
def classify_intent(state: AgentState) -> AgentState:
    """
    Classify user intent using LLM
    - Task creation
    - Task query
    - Task update
    - General conversation
    """
    last_message = state["messages"][-1].content
    
    # Use LLM to classify
    intent_prompt = f"""
    Classify the following user message:
    "{last_message}"
    
    Categories: create_task, update_task, query_tasks, general_chat
    """
    
    intent = llm.invoke(intent_prompt)
    state["metadata"]["intent"] = intent
    
    return state
```

### 3. Tool Execution Node

**Purpose**: Execute appropriate tools based on intent

```python
def execute_tools(state: AgentState) -> AgentState:
    """
    Execute relevant tools
    - add_task
    - update_task
    - list_tasks
    - delete_task
    """
    intent = state["metadata"]["intent"]
    
    if intent == "create_task":
        result = add_task.invoke(state)
    elif intent == "update_task":
        result = update_task.invoke(state)
    elif intent == "query_tasks":
        result = list_tasks.invoke(state)
    
    state["metadata"]["tool_result"] = result
    return state
```

### 4. Response Generation Node

**Purpose**: Generate natural language response

```python
def generate_response(state: AgentState) -> AgentState:
    """
    Generate human-friendly response
    - Summarize tool results
    - Provide context
    - Suggest next actions
    """
    tool_result = state["metadata"].get("tool_result")
    
    response_prompt = f"""
    Based on the following action result:
    {tool_result}
    
    Generate a helpful response to the user.
    """
    
    response = llm.invoke(response_prompt)
    state["messages"].append(AIMessage(content=response))
    
    return state
```

## Task Management Tools

### Tool: add_task

**Purpose**: Create a new task

```python
@tool
def add_task(
    name: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
) -> str:
    """
    Add a new task for the current user.
    
    Args:
        name: Task name
        description: Detailed description
        priority: low|medium|high|urgent
        tags: Optional tags for categorization
    
    Returns:
        Success message with task ID
    """
    user_id = _require_user()
    
    task = Task(
        task_id=uuid4(),
        user_id=user_id,
        name=name,
        description=description or "",
        priority=Priority(priority),
        status=TaskStatus.NOT_STARTED,
        tags=tags or [],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _TASK_STORE[task.task_id] = task
    logger.info(f"Created task {task.task_id} for user {user_id}")
    
    return f"Task '{name}' created successfully with ID {task.task_id}"
```

### Tool: update_task

**Purpose**: Modify an existing task

```python
@tool
def update_task(
    task_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """
    Update an existing task.
    
    Args:
        task_id: UUID of task to update
        name: New name (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)
    
    Returns:
        Success message
    """
    user_id = _require_user()
    task_uuid = UUID(task_id)
    
    if task_uuid not in _TASK_STORE:
        return f"Task {task_id} not found"
    
    task = _TASK_STORE[task_uuid]
    
    # Verify ownership
    if task.user_id != user_id:
        return "Access denied"
    
    # Update fields
    if name:
        task.name = name
    if description:
        task.description = description
    if status:
        task.status = TaskStatus(status)
    if priority:
        task.priority = Priority(priority)
    
    task.updated_at = datetime.now()
    
    return f"Task '{task.name}' updated successfully"
```

### Tool: list_tasks

**Purpose**: Query tasks with filters

```python
@tool
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """
    List tasks with optional filters.
    
    Args:
        status: Filter by status (optional)
        priority: Filter by priority (optional)
        tags: Filter by tags (optional)
    
    Returns:
        Formatted list of tasks
    """
    user_id = _require_user()
    
    # Filter tasks
    user_tasks = [
        task for task in _TASK_STORE.values()
        if task.user_id == user_id
    ]
    
    if status:
        user_tasks = [t for t in user_tasks if t.status.value == status]
    if priority:
        user_tasks = [t for t in user_tasks if t.priority.value == priority]
    if tags:
        user_tasks = [t for t in user_tasks if any(tag in t.tags for tag in tags)]
    
    # Format response
    if not user_tasks:
        return "No tasks found matching the criteria"
    
    result = f"Found {len(user_tasks)} tasks:\n"
    for task in user_tasks:
        result += f"\n- {task.name} [{task.status.value}] ({task.priority.value})"
    
    return result
```

### Tool: delete_task

**Purpose**: Remove a task

```python
@tool
def delete_task(task_id: str) -> str:
    """
    Delete a task by ID.
    
    Args:
        task_id: UUID of task to delete
    
    Returns:
        Success message
    """
    user_id = _require_user()
    task_uuid = UUID(task_id)
    
    if task_uuid not in _TASK_STORE:
        return f"Task {task_id} not found"
    
    task = _TASK_STORE[task_uuid]
    
    # Verify ownership
    if task.user_id != user_id:
        return "Access denied"
    
    del _TASK_STORE[task_uuid]
    logger.info(f"Deleted task {task_id} for user {user_id}")
    
    return f"Task '{task.name}' deleted successfully"
```

## LLM Configuration

### Provider Setup

```python
# llm_config.py

import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def get_llm(provider: str = "openai"):
    """
    Get configured LLM instance
    
    Args:
        provider: "openai" or "anthropic"
    
    Returns:
        Configured LLM instance
    """
    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            temperature=0.7,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

### Model Selection

| Provider | Model | Use Case | Cost |
|----------|-------|----------|------|
| OpenAI | GPT-4 | Complex reasoning | $$$ |
| OpenAI | GPT-3.5-Turbo | Fast responses | $ |
| Anthropic | Claude 3 Opus | Deep analysis | $$$ |
| Anthropic | Claude 3 Sonnet | Balanced | $$ |

## Agent Builder

### Factory Pattern

```python
# builder.py

class AgentBuilder:
    """Factory for creating configured agent instances"""
    
    @staticmethod
    def build(
        llm_provider: str = "openai",
        user_id: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> BehflowAgent:
        """
        Build a configured agent instance
        
        Args:
            llm_provider: LLM provider name
            user_id: User UUID for context
            config: Additional configuration
        
        Returns:
            Configured BehflowAgent instance
        """
        # Get LLM
        llm = get_llm(llm_provider)
        
        # Get tools
        tools = [add_task, update_task, list_tasks, delete_task]
        
        # Create agent
        agent = BehflowAgent(
            llm=llm,
            tools=tools,
            user_id=user_id,
            config=config or {}
        )
        
        return agent
```

### Usage Example

```python
from behflow_agent.builder import AgentBuilder

# Build agent for specific user
agent = AgentBuilder.build(
    llm_provider="openai",
    user_id="123e4567-e89b-12d3-a456-426614174000"
)

# Invoke with message
response = await agent.ainvoke(
    "Create a task to review project documentation with high priority",
    session_id="chat-session-1"
)

print(response["messages"][-1].content)
```

## Automated Processes

### Process Types

1. **Task Rescheduling**: Automatically reschedule overdue tasks
2. **Priority Adjustment**: Update priorities based on deadlines
3. **Reminder System**: Send notifications for upcoming tasks
4. **Analytics**: Generate task completion reports

### Process Execution

```python
# models/automated_process.py

class RescheduleTasksProcess(AutomatedProcessBase):
    """Reschedule overdue tasks to today"""
    
    @classmethod
    def execute(cls, db: Session, process_id: str) -> ProcessExecutionResult:
        """
        Execute rescheduling logic
        
        Args:
            db: Database session
            process_id: Process UUID
        
        Returns:
            Execution result with statistics
        """
        # Find overdue tasks
        overdue_tasks = db.query(TaskModel).filter(
            TaskModel.due_date < datetime.now(),
            TaskModel.status != TaskStatus.COMPLETED
        ).all()
        
        # Reschedule each task
        rescheduled_count = 0
        for task in overdue_tasks:
            task.due_date = datetime.now() + timedelta(days=1)
            rescheduled_count += 1
        
        db.commit()
        
        return ProcessExecutionResult(
            success=True,
            message=f"Rescheduled {rescheduled_count} overdue tasks",
            metadata={"count": rescheduled_count}
        )
```

## User Context Management

### Context Loading

```python
# users.py

def load_user_context(user_id: str) -> Dict[str, Any]:
    """
    Load user context including preferences and history
    
    Args:
        user_id: User UUID
    
    Returns:
        User context dictionary
    """
    # Load from database or cache
    user_data = get_user_from_db(user_id)
    
    # Load task statistics
    task_stats = get_user_task_stats(user_id)
    
    # Load preferences
    preferences = get_user_preferences(user_id)
    
    return {
        "user_id": user_id,
        "username": user_data.username,
        "task_count": task_stats["total"],
        "completed_count": task_stats["completed"],
        "preferences": preferences
    }
```

### Context Usage

The agent uses user context to:
- Personalize responses
- Suggest relevant tasks
- Apply user preferences (time zone, date format)
- Track conversation history

## Error Handling

### Graceful Degradation

```python
def safe_tool_execution(tool, *args, **kwargs):
    """
    Execute tool with error handling
    
    Returns:
        Tool result or error message
    """
    try:
        return tool.invoke(*args, **kwargs)
    except ValueError as e:
        logger.warning(f"Tool validation error: {e}")
        return f"Invalid input: {e}"
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return "An error occurred. Please try again."
```

## Performance Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_tasks(user_id: str) -> List[Task]:
    """Cached task retrieval"""
    return [task for task in _TASK_STORE.values() 
            if task.user_id == UUID(user_id)]
```

### Async Operations

```python
async def ainvoke_with_streaming(
    agent: BehflowAgent,
    message: str,
    session_id: str
) -> AsyncIterator[str]:
    """Stream agent responses for better UX"""
    async for chunk in agent.astream(message, session_id):
        if "messages" in chunk:
            yield chunk["messages"][-1].content
```

## Testing

### Unit Tests

```python
import pytest
from behflow_agent.tools import add_task, set_current_user

def test_add_task():
    """Test task creation"""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    set_current_user(user_id)
    
    result = add_task.invoke({
        "name": "Test Task",
        "description": "Test description",
        "priority": "high"
    })
    
    assert "created successfully" in result
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_agent_workflow():
    """Test complete agent interaction"""
    agent = AgentBuilder.build(user_id="test-user")
    
    response = await agent.ainvoke(
        "Create a task called 'Review code' with high priority"
    )
    
    assert "Review code" in response["messages"][-1].content
```

## Monitoring

### Logging

```python
from shared.logger import get_logger

logger = get_logger(__name__)

logger.info("Agent invoked", extra={
    "user_id": user_id,
    "session_id": session_id,
    "message_length": len(message)
})
```

### Metrics

- Response time
- Token usage
- Tool invocation count
- Error rate
- User satisfaction

## Future Enhancements

- [ ] Multi-agent collaboration
- [ ] Long-term memory with vector DB
- [ ] Voice interface support
- [ ] Proactive task suggestions
- [ ] Integration with external calendars
- [ ] Custom tool creation by users
- [ ] Agent personality customization
