"""
Main LangGraph agent definition with async support and proper node structure.
"""
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from behflow_agent.models import AgentState
from behflow_agent.nodes import should_continue, create_llm_node, create_tool_node
from behflow_agent.llm_config import LLMConfig, create_llm
from shared.logger import get_logger

logger = get_logger(__name__)


class BehflowAgent:
    """
    Main LangGraph agent class with full async support.
    
    Architecture:
    - LLM Node: Invokes language model with tool binding
    - Tool Node: Executes tool calls from LLM
    - Conditional routing: Determines flow based on tool calls
    - Full async/await support throughout
    
    Graph Flow:
    1. User message -> LLM Node
    2. LLM Node -> (tools exist?) -> Tool Node -> back to LLM Node
    3. LLM Node -> (no tools?) -> END
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Initialize the agent and build the graph.
        
        Args:
            llm_config: Optional LLM configuration. If None, uses defaults.
        """
        self.llm_config = llm_config or LLMConfig()
        self.llm = create_llm(self.llm_config)
        self.graph = None
        self.compiled_graph = None
        self._build_graph()
    
    def _build_graph(self):
        """
        Build the LangGraph computation graph with proper async nodes.
        
        Graph structure:
        1. llm_node: Async LLM invocation with tool binding
        2. tool_node: Async tool execution
        3. Conditional routing: should_continue determines next step
        4. Loop: Tools -> LLM until no more tool calls
        """
        logger.info("Building agent graph")
        
        # Create the graph with AgentState
        workflow = StateGraph(AgentState)
        
        # Create nodes
        llm_node = create_llm_node(self.llm)
        tool_node = create_tool_node()
        
        # Add nodes to graph
        # Note: LangGraph will automatically detect and use async methods
        workflow.add_node("agent", llm_node)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges from agent
        # Routes to "tools" if tool calls exist, otherwise "end"
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END,
            }
        )
        
        # Add edge from tools back to agent for iterative tool calling
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        self.compiled_graph = workflow.compile()
        self.graph = workflow
        
        logger.info("Agent graph compiled successfully")
    
    def invoke(self, message: str, user_id: Optional[str] = None) -> str:
        """
        Synchronous invoke the agent with a user message.
        
        Args:
            message: User input message
            user_id: Optional user identifier (UUID string)
            
        Returns:
            Agent response string
            
        Example:
            >>> agent = BehflowAgent()
            >>> response = agent.invoke("Create a task to review code", user_id="user123")
        """
        logger.info(f"Invoking agent with message: {message[:50]}...")
        
        if not self.compiled_graph:
            logger.error("Graph not compiled")
            return "Error: Graph not compiled"
        
        # Resolve and set current user context if needed
        uid_str = None
        if user_id:
            from behflow_agent.users import get_or_create_user_uuid
            uid = get_or_create_user_uuid(user_id)
            uid_str = str(uid)
            logger.debug(f"User context set: {uid_str}")

        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            user_id=uid_str,
        )

        try:
            # Run the graph
            result = self.compiled_graph.invoke(initial_state)
            
            # Extract the last message
            if result and "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                logger.info("Agent invocation completed successfully")
                return last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            logger.warning("No messages in result")
            return "No response generated"
            
        except Exception as e:
            logger.error(f"Error during invocation: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    async def ainvoke(self, message: str, user_id: Optional[str] = None) -> str:
        """
        Async invoke the agent with a user message.
        
        This is the preferred method for async contexts (e.g., FastAPI, async web apps).
        All nodes execute asynchronously for better performance.
        
        Args:
            message: User input message
            user_id: Optional user identifier (UUID string)
            
        Returns:
            Agent response string
            
        Example:
            >>> agent = BehflowAgent()
            >>> response = await agent.ainvoke("List my tasks", user_id="user123")
        """
        logger.info(f"Async invoking agent with message: {message[:50]}...")
        
        if not self.compiled_graph:
            logger.error("Graph not compiled")
            return "Error: Graph not compiled"
        
        # Resolve and set current user context if needed
        uid_str = None
        if user_id:
            from behflow_agent.users import get_or_create_user_uuid
            uid = get_or_create_user_uuid(user_id)
            uid_str = str(uid)
            logger.debug(f"User context set: {uid_str}")
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            user_id=uid_str,
        )
        
        try:
            # Run the graph asynchronously
            result = await self.compiled_graph.ainvoke(initial_state)
            
            # Extract the last message
            if result and "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                logger.info("Async agent invocation completed successfully")
                return last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            logger.warning("No messages in result")
            return "No response generated"
            
        except Exception as e:
            logger.error(f"Error during async invocation: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    async def astream(self, message: str, user_id: Optional[str] = None):
        """
        Async stream the agent responses.
        
        Yields intermediate states as the graph executes, useful for
        streaming responses in real-time applications.
        
        Args:
            message: User input message
            user_id: Optional user identifier
            
        Yields:
            Intermediate state updates from the graph execution
            
        Example:
            >>> async for chunk in agent.astream("Create a task"):
            ...     print(chunk)
        """
        logger.info(f"Async streaming agent with message: {message[:50]}...")
        
        if not self.compiled_graph:
            logger.error("Graph not compiled")
            yield {"error": "Graph not compiled"}
            return
        
        # Resolve user context
        uid_str = None
        if user_id:
            from behflow_agent.users import get_or_create_user_uuid
            uid = get_or_create_user_uuid(user_id)
            uid_str = str(uid)
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            user_id=uid_str,
        )
        
        try:
            # Stream the graph execution
            async for chunk in self.compiled_graph.astream(initial_state):
                yield chunk
        except Exception as e:
            logger.error(f"Error during streaming: {e}", exc_info=True)
            yield {"error": str(e)}
