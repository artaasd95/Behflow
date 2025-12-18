from typing import TypedDict


class AgentState(TypedDict):
    """State schema for the agent graph"""
    messages: list
    current_step: str
