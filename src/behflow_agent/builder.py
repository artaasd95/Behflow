"""
Agent Builder - Factory pattern for creating agent instances
"""
from behflow_agent.agent import BehflowAgent


class AgentBuilder:
    """
    Factory class for building and configuring agent instances
    Implements the Factory pattern
    """
    
    @staticmethod
    def build(config: dict | None = None) -> BehflowAgent:
        """
        Build and return a configured agent instance
        
        Args:
            config: Optional configuration dictionary for the agent
            
        Returns:
            Configured BehflowAgent instance
        """
        # TODO: Add configuration logic, environment setup, etc.
        agent = BehflowAgent()
        return agent
    
    @staticmethod
    def build_with_custom_nodes(nodes: list) -> BehflowAgent:
        """
        Build agent with custom node configuration
        
        Args:
            nodes: List of custom nodes to include in the graph
            
        Returns:
            Configured BehflowAgent instance
        """
        # TODO: Implement custom node injection
        agent = BehflowAgent()
        return agent
