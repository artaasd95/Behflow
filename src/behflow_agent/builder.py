"""
Agent Builder - Factory pattern for creating agent instances with configuration.
"""
from typing import Optional, Dict, Any
from behflow_agent.agent import BehflowAgent
from behflow_agent.llm_config import LLMConfig
from shared.logger import get_logger

logger = get_logger(__name__)


class AgentBuilder:
    """
    Factory class for building and configuring agent instances.
    Implements the Builder/Factory pattern for flexible agent creation.
    """
    
    @staticmethod
    def build(config: Optional[Dict[str, Any]] = None) -> BehflowAgent:
        """
        Build and return a configured agent instance.
        
        Args:
            config: Optional configuration dictionary with keys:
                - model_name: LLM model identifier
                - temperature: Sampling temperature
                - max_tokens: Maximum response tokens
                - api_key: API key for LLM provider
                - base_url: Base URL for LLM API
            
        Returns:
            Configured BehflowAgent instance
            
        Example:
            >>> config = {
            ...     "model_name": "openai/gpt-4o-mini",
            ...     "temperature": 0.7,
            ...     "api_key": "sk-xxx"
            ... }
            >>> agent = AgentBuilder.build(config)
        """
        logger.info("Building agent with config: %s", config)
        
        if config:
            # Create LLM config from dict
            llm_config = LLMConfig(
                model_name=config.get("model_name", "openai/gpt-4o-mini"),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens"),
                api_key=config.get("api_key"),
                base_url=config.get("base_url"),
            )
            agent = BehflowAgent(llm_config=llm_config)
        else:
            # Use default configuration
            agent = BehflowAgent()
        
        logger.info("Agent built successfully")
        return agent
    
    @staticmethod
    def build_with_llm_config(llm_config: LLMConfig) -> BehflowAgent:
        """
        Build agent with a specific LLM configuration object.
        
        Args:
            llm_config: LLMConfig instance
            
        Returns:
            Configured BehflowAgent instance
            
        Example:
            >>> from behflow_agent.llm_config import LLMConfig
            >>> llm_config = LLMConfig(model_name="openai/gpt-4o", temperature=0.5)
            >>> agent = AgentBuilder.build_with_llm_config(llm_config)
        """
        logger.info("Building agent with LLM config: %s", llm_config.model_name)
        agent = BehflowAgent(llm_config=llm_config)
        logger.info("Agent built successfully")
        return agent
    
    @staticmethod
    def build_default() -> BehflowAgent:
        """
        Build agent with default configuration (OpenRouter with GPT-4o-mini).
        
        Returns:
            BehflowAgent with default settings
            
        Example:
            >>> agent = AgentBuilder.build_default()
        """
        logger.info("Building agent with default configuration")
        return BehflowAgent()
