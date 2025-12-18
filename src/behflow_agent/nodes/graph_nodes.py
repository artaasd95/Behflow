"""
Agent nodes for the LangGraph workflow.
Includes LLM invocation node and tool calling nodes with async support.
"""
from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import ToolNode
from behflow_agent.models.models import AgentState
from behflow_agent.tools import TASK_TOOLS, set_current_user, clear_current_user
from behflow_agent.utils import AGENT_PROMPT
from shared.logger import get_logger

logger = get_logger(__name__)


class LLMNode:
    """
    LLM Invocation Node with async support.
    
    This node:
    - Takes the current state with message history
    - Invokes the LLM with bound tools
    - Returns updated state with the AI response
    - Supports both sync and async execution
    """
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the LLM node.
        
        Args:
            llm: Initialized chat model (from init_chat_model)
        """
        self.llm = llm
        # Bind tools to the LLM for function calling
        self.llm_with_tools = llm.bind_tools(TASK_TOOLS)
        logger.info(f"LLM node initialized with {len(TASK_TOOLS)} tools")
    
    async def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Async invocation of the LLM node.
        
        Args:
            state: Current agent state with message history
            
        Returns:
            Dictionary with new messages to add to state
        """
        return await self.ainvoke(state)
    
    async def ainvoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Async invoke the LLM with current state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state dict with AI response
        """
        logger.debug(f"LLM node processing {len(state.messages)} messages")
        
        try:
            # Set user context for tools
            if state.user_id:
                set_current_user(state.user_id)
            
            # Format messages with prompt template
            formatted_messages = AGENT_PROMPT.format_messages(
                messages=state.messages
            )
            
            # Invoke LLM with tools bound
            response = await self.llm_with_tools.ainvoke(formatted_messages)
            
            logger.info(f"LLM responded with {len(response.content) if isinstance(response.content, str) else 'structured'} content")
            
            # Check if there are tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"LLM requested {len(response.tool_calls)} tool calls")
            
            return {"messages": [response]}
            
        except Exception as e:
            logger.error(f"Error in LLM node: {e}", exc_info=True)
            # Return error message
            error_msg = AIMessage(
                content=f"I encountered an error: {str(e)}. Please try again."
            )
            return {"messages": [error_msg]}
        finally:
            # Clear user context
            clear_current_user()
    
    def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Synchronous invoke (wraps async).
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state dict with AI response
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.ainvoke(state))


class ToolCallNode:
    """
    Tool Calling Node using LangGraph's ToolNode.
    
    This node:
    - Executes tool calls from the LLM response
    - Supports async execution
    - Returns tool results as messages
    """
    
    def __init__(self):
        """Initialize the tool call node."""
        # Use LangGraph's prebuilt ToolNode for tool execution
        self.tool_node = ToolNode(TASK_TOOLS)
        logger.info(f"Tool call node initialized with {len(TASK_TOOLS)} tools")
    
    async def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        Async invocation of the tool node.
        
        Args:
            state: Current agent state with tool calls
            
        Returns:
            Dictionary with tool result messages
        """
        return await self.ainvoke(state)
    
    async def ainvoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Async execute tools.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state dict with tool results
        """
        logger.debug("Tool call node processing tools")
        
        try:
            # Set user context for tools
            if state.user_id:
                set_current_user(state.user_id)
            
            # Execute tools using LangGraph's ToolNode
            # ToolNode automatically extracts tool calls from messages
            result = await self.tool_node.ainvoke(state)
            
            logger.info("Tool execution completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in tool call node: {e}", exc_info=True)
            # Return error message
            from langchain_core.messages import ToolMessage
            error_msg = ToolMessage(
                content=f"Tool execution failed: {str(e)}",
                tool_call_id="error"
            )
            return {"messages": [error_msg]}
        finally:
            # Clear user context
            clear_current_user()
    
    def invoke(self, state: AgentState) -> Dict[str, Any]:
        """
        Synchronous invoke (wraps async).
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state dict with tool results
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.ainvoke(state))


def should_continue(state: AgentState) -> str:
    """
    Routing function to determine next node.
    
    Args:
        state: Current agent state
        
    Returns:
        "tools" if there are tool calls to execute, "end" otherwise
    """
    messages = state.messages
    last_message = messages[-1]
    
    # Check if the last message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.debug(f"Routing to tools ({len(last_message.tool_calls)} calls)")
        return "tools"
    
    logger.debug("Routing to end")
    return "end"


def create_llm_node(llm: BaseChatModel) -> LLMNode:
    """
    Factory function to create an LLM node.
    
    Args:
        llm: Initialized chat model
        
    Returns:
        Configured LLM node
    """
    return LLMNode(llm)


def create_tool_node() -> ToolCallNode:
    """
    Factory function to create a tool call node.
    
    Returns:
        Configured tool call node
    """
    return ToolCallNode()
