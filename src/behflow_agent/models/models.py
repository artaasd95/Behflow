from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class AgentState(BaseModel):
    """State schema for the agent graph.
    
    Uses LangGraph's add_messages reducer for message history management.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str | None = None
