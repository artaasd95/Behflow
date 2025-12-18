# Behflow Agent Service

LangGraph-based agent service for orchestrating conversational workflows.

## Structure

```
behflow_agent/
├── nodes/
│   └── __init__.py       # Node definitions (BaseNode, ProcessingNode, etc.)
├── agent.py              # Main LangGraph agent class
├── builder.py            # Factory pattern for building agents
└── __init__.py
```

## Architecture

- **Nodes**: Individual processing units that execute specific tasks
- **Agent**: Main graph orchestrator using LangGraph
- **Builder**: Factory pattern for creating configured agent instances

## Usage (from backend)

```python
from behflow_agent.builder import AgentBuilder

# Build agent
agent = AgentBuilder.build()

# Invoke agent
response = await agent.ainvoke("Hello", session_id="123")
```

## TODO

- Implement actual LangGraph graph construction
- Add real node logic and state management
- Integrate LLM providers (OpenAI, Anthropic, etc.)
- Add Task model tests and edge case validation (timezone/jalali conversion)

## Models

- `AgentState` — agent runtime state (in `models.models`)
- `Task` — task domain model (in `models.task`) — includes Gregorian and Jalali date fields, timezone aware defaults, priority and status enums

