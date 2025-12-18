# Behflow Agent

LangGraph-based conversational AI agent for task management with full async support and OpenRouter integration.

## Features

- ✅ **LangGraph Architecture**: Modern graph-based agent workflow
- ✅ **Async Support**: Full async/await implementation for high performance
- ✅ **Tool Calling**: Automatic tool discovery and execution
- ✅ **OpenRouter Integration**: Uses OpenRouter for flexible model access
- ✅ **Prompt Templates**: Pre-built templates for task management
- ✅ **State Management**: Proper state handling with message history
- ✅ **Streaming Support**: Real-time response streaming

## Architecture

### Graph Structure

```
User Message
    ↓
[LLM Node] ← ─ ─ ─ ─ ─ ┐
    ↓                    │
Has Tool Calls?          │
    ↓ (yes)              │
[Tool Node]  ─ ─ ─ ─ ─ ─┘
    ↓ (no)
   END
```

### Components

#### 1. **LLM Node** (`nodes/graph_nodes.py`)
- Invokes language model with prompt templates
- Binds tools for function calling
- Supports async invocation
- Handles errors gracefully

#### 2. **Tool Node** (`nodes/graph_nodes.py`)
- Executes tool calls from LLM
- Uses LangGraph's ToolNode
- Async tool execution
- User context management

#### 3. **Agent** (`agent.py`)
- Main orchestrator class
- Compiles and manages graph
- Provides `invoke()`, `ainvoke()`, and `astream()` methods
- Handles state initialization

#### 4. **LLM Config** (`llm_config.py`)
- Configuration management for LLM
- OpenRouter adapter setup
- Uses `init_chat_model` for flexibility
- Environment variable support

#### 5. **Utils** (`utils.py`)
- Prompt templates
- Helper functions
- Task formatting utilities

## Installation

```bash
cd src/behflow_agent
pip install -r requirements.txt
```

## Configuration

### Environment Variables

```bash
# Required: OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."

# Optional: Custom base URL
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"

# Alternative: Use OpenAI directly
export OPENAI_API_KEY="sk-..."
```

### LLM Configuration

```python
from behflow_agent.llm_config import LLMConfig

# OpenRouter with GPT-4o-mini (default)
config = LLMConfig(
    model_name="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=2000
)

# Other models via OpenRouter
config = LLMConfig(
    model_name="anthropic/claude-3-5-sonnet",
    temperature=0.5
)
```

## Usage

### Basic Usage

```python
from behflow_agent import BehflowAgent

# Create agent with default config
agent = BehflowAgent()

# Synchronous invocation
response = agent.invoke("Create a task to review PRs", user_id="user123")
print(response)

# Async invocation (recommended)
response = await agent.ainvoke("List my tasks", user_id="user123")
print(response)
```

### With Custom Configuration

```python
from behflow_agent import BehflowAgent
from behflow_agent.llm_config import LLMConfig

# Create custom config
config = LLMConfig(
    model_name="openai/gpt-4o",
    temperature=0.5,
    max_tokens=1500
)

# Create agent
agent = BehflowAgent(llm_config=config)
response = await agent.ainvoke("Help me organize my tasks")
```

### Using the Builder Pattern

```python
from behflow_agent import AgentBuilder

# Build with dict config
config = {
    "model_name": "openai/gpt-4o-mini",
    "temperature": 0.7,
    "api_key": "sk-..."
}
agent = AgentBuilder.build(config)

# Or use default
agent = AgentBuilder.build_default()
```

### Streaming Responses

```python
async for chunk in agent.astream("Create three tasks for today"):
    print(chunk)
```

## Available Tools

The agent has access to these task management tools:

- `add_task`: Create a new task with name, description, priority, tags
- `remove_task`: Delete a task by ID
- `change_task_priority`: Update task priority
- `update_task`: Modify task details
- `list_tasks`: Get all user tasks
- `search_tasks`: Find tasks by criteria

## Examples

### Example 1: Create Task
```python
response = await agent.ainvoke(
    "Create a high priority task to review the authentication module",
    user_id="user123"
)
# Agent will automatically call add_task tool
```

### Example 2: List and Filter
```python
response = await agent.ainvoke(
    "Show me all high priority tasks",
    user_id="user123"
)
# Agent will call list_tasks and filter results
```

### Example 3: Complex Operations
```python
response = await agent.ainvoke(
    "Create tasks for: 1) Code review, 2) Write tests, 3) Update docs. All high priority.",
    user_id="user123"
)
# Agent will make multiple tool calls
```

## Async Best Practices

1. **Always use `ainvoke` in async contexts**:
   ```python
   response = await agent.ainvoke(message)  # ✅ Good
   response = agent.invoke(message)         # ❌ Blocks event loop
   ```

2. **Use streaming for real-time responses**:
   ```python
   async for chunk in agent.astream(message):
       # Process chunks as they arrive
       pass
   ```

3. **Initialize once, reuse**:
   ```python
   # At startup
   agent = BehflowAgent()
   
   # For each request
   response = await agent.ainvoke(message)
   ```

## Extending the Agent

### Add Custom Tools

```python
from langchain_core.tools import tool

@tool
def custom_tool(param: str) -> str:
    """Custom tool description."""
    return f"Processed: {param}"

# Add to TASK_TOOLS in tools.py
```

### Custom Prompt Templates

```python
from behflow_agent.utils import create_custom_prompt

custom_prompt = create_custom_prompt(
    "You are a specialized agent for..."
)
```

## Development

### Project Structure

```
behflow_agent/
├── __init__.py          # Package exports
├── agent.py             # Main agent class
├── builder.py           # Factory pattern builder
├── llm_config.py        # LLM configuration
├── utils.py             # Utilities and prompts
├── tools.py             # Tool definitions
├── users.py             # User management
├── models/              # Pydantic models
│   ├── models.py        # AgentState
│   ├── task.py          # Task model
│   └── automated_process.py
└── nodes/               # Graph nodes
    ├── __init__.py
    └── graph_nodes.py   # LLM & Tool nodes
```

### Running Tests

```python
# Test LLM connection
from behflow_agent.llm_config import create_llm, test_llm_connection

llm = create_llm()
success = await test_llm_connection(llm)
```

## Troubleshooting

### Issue: "No API key found"
**Solution**: Set `OPENROUTER_API_KEY` or `OPENAI_API_KEY` environment variable

### Issue: "Graph not compiled"
**Solution**: Ensure agent initialization completed without errors

### Issue: Tool execution fails
**Solution**: Check that `user_id` is provided for user-specific operations

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Chat Models](https://python.langchain.com/docs/modules/model_io/chat/)
- [OpenRouter API](https://openrouter.ai/docs)
