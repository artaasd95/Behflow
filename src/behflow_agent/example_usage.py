"""
Example usage of the Behflow Agent with async support.

This demonstrates:
- Basic agent initialization
- Async invocation
- Streaming responses
- Custom configuration
"""
import asyncio
import os
from behflow_agent import BehflowAgent, AgentBuilder, LLMConfig


async def example_basic_usage():
    """Example 1: Basic async usage with default configuration."""
    print("\n=== Example 1: Basic Usage ===")
    
    # Create agent with defaults (OpenRouter + GPT-4o-mini)
    agent = BehflowAgent()
    
    # Async invoke
    response = await agent.ainvoke(
        "Create a high priority task to review the new API endpoints",
        user_id="user123"
    )
    print(f"Response: {response}")


async def example_custom_config():
    """Example 2: Using custom LLM configuration."""
    print("\n=== Example 2: Custom Configuration ===")
    
    # Create custom LLM config
    config = LLMConfig(
        model_name="openai/gpt-4o-mini",
        temperature=0.5,
        max_tokens=1500
    )
    
    # Create agent with custom config
    agent = BehflowAgent(llm_config=config)
    
    response = await agent.ainvoke(
        "List my current tasks",
        user_id="user123"
    )
    print(f"Response: {response}")


async def example_builder_pattern():
    """Example 3: Using AgentBuilder factory."""
    print("\n=== Example 3: Builder Pattern ===")
    
    # Build with dict config
    config = {
        "model_name": "openai/gpt-4o-mini",
        "temperature": 0.7,
    }
    agent = AgentBuilder.build(config)
    
    response = await agent.ainvoke(
        "Create three tasks: code review, write tests, update documentation",
        user_id="user123"
    )
    print(f"Response: {response}")


async def example_streaming():
    """Example 4: Streaming responses."""
    print("\n=== Example 4: Streaming Responses ===")
    
    agent = BehflowAgent()
    
    print("Streaming chunks:")
    async for chunk in agent.astream(
        "What tasks should I prioritize today?",
        user_id="user123"
    ):
        print(f"  Chunk: {chunk}")


async def example_multiple_tools():
    """Example 5: Complex multi-tool interaction."""
    print("\n=== Example 5: Multiple Tool Calls ===")
    
    agent = BehflowAgent()
    
    # This will trigger multiple tool calls
    response = await agent.ainvoke(
        """I need help organizing my work:
        1. Create a high priority task for the sprint review
        2. Create a medium priority task for updating the README
        3. Then list all my tasks
        """,
        user_id="user123"
    )
    print(f"Response: {response}")


async def example_sync_usage():
    """Example 6: Synchronous usage (not recommended)."""
    print("\n=== Example 6: Synchronous Usage ===")
    
    agent = BehflowAgent()
    
    # Sync invoke (blocks the event loop, use only when necessary)
    response = agent.invoke(
        "Create a task to review code",
        user_id="user123"
    )
    print(f"Response: {response}")


async def main():
    """Run all examples."""
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No API key found!")
        print("Set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable")
        print("\nExample:")
        print('  export OPENROUTER_API_KEY="sk-or-v1-..."')
        return
    
    print("🚀 Behflow Agent Examples")
    print("=" * 50)
    
    try:
        # Run examples
        await example_basic_usage()
        await example_custom_config()
        await example_builder_pattern()
        await example_streaming()
        await example_multiple_tools()
        
        # Sync example (run last as it might block)
        example_sync_usage()
        
        print("\n✅ All examples completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
