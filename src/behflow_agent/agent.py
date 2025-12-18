"""
Main LangGraph agent definition
"""
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from behflow_agent.models import AgentState
from behflow_agent.tools import TASK_TOOLS


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Routing function to determine if we should call tools or end.
    
    Args:
        state: Current agent state
        
    Returns:
        "tools" if the last message has tool calls, "end" otherwise
    """
    messages = state.messages
    last_message = messages[-1]
    
    # If there are tool calls, route to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end the conversation
    return "end"


def call_model(state: AgentState) -> dict:
    """LLM invocation node (placeholder for now).
    
    This node will call the LLM with the current state and bound tools.
    For now, it returns a placeholder response.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state dict with new message
    """
    # TODO: Replace with actual LLM invocation
    # Example:
    # model = ChatOpenAI(model="gpt-4")
    # model_with_tools = model.bind_tools(TASK_TOOLS)
    # response = model_with_tools.invoke(state.messages)
    
    # Placeholder response
    last_message = state.messages[-1]
    response = AIMessage(
        content=f"[Placeholder] I received your message: {last_message.content}. LLM integration coming soon."
    )
    
    return {"messages": [response]}


class BehflowAgent:
    """
    Main LangGraph agent class
    Orchestrates the conversation flow through the graph
    """
    
    def __init__(self):
        """Initialize the agent and build the graph"""
        self.graph = None
        self.compiled_graph = None
        self._build_graph()
    
    def _build_graph(self):
        """
        Build the LangGraph computation graph with tool calling
        
        Graph structure:
        1. call_model node: Invokes LLM (placeholder)
        2. tools node: Executes tools if LLM requests them
        3. Conditional routing based on tool calls
        """
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(TASK_TOOLS))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END,
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        self.compiled_graph = workflow.compile()
        self.graph = workflow
    
    def invoke(self, message: str, user_id: str | None = None) -> str:
        """
        Invoke the agent with a user message
        
        Args:
            message: User input message
            user_id: Optional user identifier
            
        Returns:
            Agent response string
        """
        if not self.compiled_graph:
            return "Error: Graph not compiled"
        
        # Resolve and set current user context
        if user_id:
            from behflow_agent.users import get_or_create_user_uuid
            from behflow_agent.tools import set_current_user
            uid = get_or_create_user_uuid(user_id)
            set_current_user(str(uid))

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": str(uid) if user_id else None,
        }

        # Run the graph
        result = self.compiled_graph.invoke(initial_state)

        # Clear user context after invocation
        from behflow_agent.tools import clear_current_user
        clear_current_user()
        
        # Extract the last message
        if result and "messages" in result:
            last_message = result["messages"][-1]
            return last_message.content
        
        return "No response generated"
    
    async def ainvoke(self, message: str, user_id: str | None = None) -> str:
        """
        Async invoke the agent
        
        Args:
            message: User input message
            user_id: Optional user identifier
            
        Returns:
            Agent response string
        """
        if not self.compiled_graph:
            return "Error: Graph not compiled"
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
        }
        
        # Run the graph asynchronously
        result = await self.compiled_graph.ainvoke(initial_state)

        # Clear user context after invocation
        from behflow_agent.tools import clear_current_user
        clear_current_user()
        
        # Extract the last message
        if result and "messages" in result:
            last_message = result["messages"][-1]
            return last_message.content
        
        return "No response generated"
