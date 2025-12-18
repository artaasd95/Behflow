"""
LLM configuration and initialization for Behflow agent.
Supports OpenRouter and other providers via langchain's init_chat_model.
"""
import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from shared.logger import get_logger

logger = get_logger(__name__)


class LLMConfig:
    """Configuration for LLM initialization."""
    
    def __init__(
        self,
        model_name: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize LLM configuration.
        
        Args:
            model_name: Model identifier (e.g., "openai/gpt-4o-mini" for OpenRouter)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            api_key: API key (defaults to OPENROUTER_API_KEY env var)
            base_url: Base URL for API (defaults to OpenRouter)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        if not self.api_key:
            logger.warning("No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable.")


def create_llm(config: Optional[LLMConfig] = None) -> BaseChatModel:
    """
    Create and initialize a chat model using init_chat_model.
    
    This function uses langchain's init_chat_model which provides:
    - Unified interface for multiple providers
    - Automatic client initialization
    - Support for async operations
    
    Args:
        config: LLM configuration object. If None, uses defaults.
        
    Returns:
        Initialized BaseChatModel instance
        
    Example:
        >>> config = LLMConfig(model_name="openai/gpt-4o-mini", temperature=0.7)
        >>> llm = create_llm(config)
        >>> response = await llm.ainvoke("Hello!")
    """
    if config is None:
        config = LLMConfig()
    
    logger.info(f"Initializing LLM: {config.model_name} (temp={config.temperature})")
    
    # Prepare kwargs for init_chat_model
    kwargs = {
        "temperature": config.temperature,
    }
    
    if config.max_tokens:
        kwargs["max_tokens"] = config.max_tokens
    
    # For OpenRouter, we use the OpenAI-compatible interface
    if "openrouter.ai" in config.base_url:
        kwargs["api_key"] = config.api_key
        kwargs["base_url"] = config.base_url
        
        # Extract the actual model name (remove provider prefix if present)
        model_name = config.model_name
        
        # Use OpenAI provider with custom base_url for OpenRouter
        try:
            llm = init_chat_model(
                model=model_name,
                model_provider="openai",
                **kwargs
            )
            logger.info(f"Successfully initialized OpenRouter model: {model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter model: {e}")
            raise
    else:
        # For other providers, use standard init_chat_model
        try:
            llm = init_chat_model(
                model=config.model_name,
                **kwargs
            )
            logger.info(f"Successfully initialized model: {config.model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise


async def test_llm_connection(llm: BaseChatModel) -> bool:
    """
    Test LLM connection with a simple async invocation.
    
    Args:
        llm: Initialized chat model
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = await llm.ainvoke("Hello")
        logger.info("LLM connection test successful")
        return True
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return False
