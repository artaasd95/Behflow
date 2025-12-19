"""
Behflow Agent - LangGraph-based agent for task management with async support.

This package provides a modern, async-first agent implementation using:
- LangGraph for graph-based workflows
- LangChain for LLM integration
- OpenRouter for flexible model access
- Full async/await support

Quick Start:
    >>> from behflow_agent import BehflowAgent
    >>> agent = BehflowAgent()
    >>> response = await agent.ainvoke("Create a task", user_id="user123")
"""
from behflow_agent.agent import BehflowAgent
from behflow_agent.builder import AgentBuilder
from behflow_agent.llm_config import LLMConfig, create_llm
from behflow_agent.models.models import AgentState
from behflow_agent.utils import get_agent_prompt, create_custom_prompt

__version__ = "0.2.0"
__all__ = [
    "BehflowAgent",
    "AgentBuilder",
    "LLMConfig",
    "create_llm",
    "AgentState",
    "get_agent_prompt",
    "create_custom_prompt",
]
