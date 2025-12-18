"""
Tests for agent tools
"""
import pytest
from uuid import UUID


class TestAgentTools:
    """Test agent task management tools"""
    
    def test_add_task_tool(self, agent_user_id):
        """Test add_task tool"""
        from src.behflow_agent.tools import add_task, set_current_user, _TASK_STORE
        
        set_current_user(agent_user_id)
        
        result = add_task.invoke({
            "name": "Test Task",
            "description": "Test description",
            "priority": "high",
            "tags": ["test", "urgent"]
        })
        
        assert "created successfully" in result.lower()
        assert "Test Task" in result
        assert len(_TASK_STORE) == 1
        
        # Verify task properties
        task = list(_TASK_STORE.values())[0]
        assert task.name == "Test Task"
        assert task.description == "Test description"
        assert task.priority.value == "high"
        assert "test" in task.tags
        assert "urgent" in task.tags
    
    def test_add_task_without_user_context(self):
        """Test add_task fails without user context"""
        from src.behflow_agent.tools import add_task
        
        with pytest.raises(ValueError, match="No current user"):
            add_task.invoke({"name": "Test Task"})
    
    def test_list_tasks_empty(self, agent_user_id):
        """Test list_tasks with no tasks"""
        from src.behflow_agent.tools import list_tasks, set_current_user
        
        set_current_user(agent_user_id)
        
        result = list_tasks.invoke({})
        
        assert "No tasks found" in result
    
    def test_list_tasks_with_tasks(self, agent_user_id):
        """Test list_tasks with multiple tasks"""
        from src.behflow_agent.tools import add_task, list_tasks, set_current_user
        
        set_current_user(agent_user_id)
        
        # Create tasks
        add_task.invoke({"name": "Task 1", "priority": "high"})
        add_task.invoke({"name": "Task 2", "priority": "medium"})
        add_task.invoke({"name": "Task 3", "priority": "low"})
        
        result = list_tasks.invoke({})
        
        assert "Found 3 tasks" in result
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result
    
    def test_list_tasks_with_status_filter(self, agent_user_id):
        """Test list_tasks with status filter"""
        from src.behflow_agent.tools import add_task, list_tasks, set_current_user, _TASK_STORE
        from src.behflow_agent.models.task import TaskStatus
        
        set_current_user(agent_user_id)
        
        # Create tasks with different statuses
        result1 = add_task.invoke({"name": "Task 1"})
        result2 = add_task.invoke({"name": "Task 2"})
        
        # Manually update status for testing
        tasks = list(_TASK_STORE.values())
        tasks[0].status = TaskStatus.NOT_STARTED
        tasks[1].status = TaskStatus.IN_PROGRESS
        
        result = list_tasks.invoke({"status": "in_progress"})
        
        assert "Found 1 tasks" in result or "Found 1 task" in result
        assert "Task 2" in result
    
    def test_update_task_tool(self, agent_user_id):
        """Test update_task tool"""
        from src.behflow_agent.tools import add_task, update_task, set_current_user, _TASK_STORE
        
        set_current_user(agent_user_id)
        
        # Create task
        result = add_task.invoke({"name": "Original Name", "priority": "low"})
        task_id = list(_TASK_STORE.keys())[0]
        
        # Update task
        result = update_task.invoke({
            "task_id": str(task_id),
            "name": "Updated Name",
            "status": "in_progress",
            "priority": "high"
        })
        
        assert "updated successfully" in result.lower()
        assert "Updated Name" in result
        
        # Verify update
        task = _TASK_STORE[task_id]
        assert task.name == "Updated Name"
        assert task.status.value == "in_progress"
        assert task.priority.value == "high"
    
    def test_update_nonexistent_task(self, agent_user_id):
        """Test updating nonexistent task"""
        from src.behflow_agent.tools import update_task, set_current_user
        from uuid import uuid4
        
        set_current_user(agent_user_id)
        
        fake_id = str(uuid4())
        result = update_task.invoke({"task_id": fake_id, "name": "Updated"})
        
        assert "not found" in result.lower()
    
    def test_delete_task_tool(self, agent_user_id):
        """Test delete_task tool"""
        from src.behflow_agent.tools import add_task, delete_task, set_current_user, _TASK_STORE
        
        set_current_user(agent_user_id)
        
        # Create task
        add_task.invoke({"name": "To Delete"})
        task_id = list(_TASK_STORE.keys())[0]
        
        assert len(_TASK_STORE) == 1
        
        # Delete task
        result = delete_task.invoke({"task_id": str(task_id)})
        
        assert "deleted successfully" in result.lower()
        assert len(_TASK_STORE) == 0
    
    def test_delete_nonexistent_task(self, agent_user_id):
        """Test deleting nonexistent task"""
        from src.behflow_agent.tools import delete_task, set_current_user
        from uuid import uuid4
        
        set_current_user(agent_user_id)
        
        fake_id = str(uuid4())
        result = delete_task.invoke({"task_id": fake_id})
        
        assert "not found" in result.lower()
    
    def test_user_context_management(self):
        """Test user context setting and clearing"""
        from src.behflow_agent.tools import set_current_user, clear_current_user, _require_user
        
        # Should raise without user
        with pytest.raises(ValueError):
            _require_user()
        
        # Set user
        set_current_user("test-user-123")
        user_id = _require_user()
        assert str(user_id) == "test-user-123"
        
        # Clear user
        clear_current_user()
        with pytest.raises(ValueError):
            _require_user()
    
    def test_task_isolation_between_users(self):
        """Test that tasks are isolated by user"""
        from src.behflow_agent.tools import add_task, list_tasks, set_current_user, clear_current_user, _TASK_STORE
        
        # User 1 creates tasks
        set_current_user("user-1")
        add_task.invoke({"name": "User 1 Task 1"})
        add_task.invoke({"name": "User 1 Task 2"})
        
        user1_result = list_tasks.invoke({})
        clear_current_user()
        
        # User 2 creates tasks
        set_current_user("user-2")
        add_task.invoke({"name": "User 2 Task 1"})
        
        user2_result = list_tasks.invoke({})
        clear_current_user()
        
        # User 1 should only see their tasks
        assert "Found 2 tasks" in user1_result
        assert "User 1 Task 1" in user1_result
        assert "User 2 Task 1" not in user1_result
        
        # User 2 should only see their task
        assert "Found 1 task" in user2_result
        assert "User 2 Task 1" in user2_result
        assert "User 1 Task 1" not in user2_result


class TestAgentBuilder:
    """Test agent builder factory"""
    
    def test_build_agent_with_defaults(self):
        """Test building agent with default configuration"""
        from src.behflow_agent.builder import AgentBuilder
        
        agent = AgentBuilder.build()
        
        assert agent is not None
        # Add more assertions based on your BehflowAgent implementation
    
    def test_build_agent_with_user_id(self):
        """Test building agent with specific user ID"""
        from src.behflow_agent.builder import AgentBuilder
        
        user_id = "test-user-123"
        agent = AgentBuilder.build(user_id=user_id)
        
        assert agent is not None
        # Verify user context is set
    
    @pytest.mark.asyncio
    async def test_agent_invocation(self):
        """Test agent invocation"""
        from src.behflow_agent.builder import AgentBuilder
        
        agent = AgentBuilder.build(user_id="test-user-123")
        
        # Simple invocation test
        # Note: This requires LLM API key in environment
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No LLM API key available")
        
        response = await agent.ainvoke(
            "Create a task called 'Agent Test Task'"
        )
        
        assert response is not None
