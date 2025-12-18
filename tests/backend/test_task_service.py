"""
Tests for task service
"""
import pytest
from datetime import datetime, timedelta
from uuid import UUID


class TestTaskService:
    """Test task service operations"""
    
    def test_create_task(self, db_session, sample_user):
        """Test task creation"""
        from src.backend.app.database.task_service import TaskService
        
        task = TaskService.create_task(
            db_session,
            user_id=sample_user.user_id,
            task_data={
                "name": "Test Task",
                "description": "Test description",
                "priority": "high",
                "status": "not_started"
            }
        )
        
        assert task is not None
        assert task.name == "Test Task"
        assert task.description == "Test description"
        assert task.priority.value == "high"
        assert task.status.value == "not_started"
        assert task.user_id == sample_user.user_id
        assert isinstance(task.task_id, UUID)
    
    def test_create_task_with_due_date(self, db_session, sample_user):
        """Test task creation with due date"""
        from src.backend.app.database.task_service import TaskService
        
        due_date = datetime.now() + timedelta(days=7)
        
        task = TaskService.create_task(
            db_session,
            user_id=sample_user.user_id,
            task_data={
                "name": "Task with due date",
                "priority": "medium",
                "due_date": due_date.isoformat()
            }
        )
        
        assert task is not None
        assert task.due_date is not None
        assert task.due_date.date() == due_date.date()
    
    def test_get_user_tasks(self, db_session, sample_user):
        """Test retrieving user tasks"""
        from src.backend.app.database.task_service import TaskService
        
        # Create multiple tasks
        TaskService.create_task(db_session, sample_user.user_id, {"name": "Task 1", "priority": "high"})
        TaskService.create_task(db_session, sample_user.user_id, {"name": "Task 2", "priority": "medium"})
        TaskService.create_task(db_session, sample_user.user_id, {"name": "Task 3", "priority": "low"})
        db_session.commit()
        
        # Retrieve all tasks
        tasks = TaskService.get_user_tasks(db_session, sample_user.user_id)
        
        assert len(tasks) == 3
        assert all(task.user_id == sample_user.user_id for task in tasks)
    
    def test_get_user_tasks_with_status_filter(self, db_session, sample_user):
        """Test retrieving tasks with status filter"""
        from src.backend.app.database.task_service import TaskService
        
        # Create tasks with different statuses
        TaskService.create_task(db_session, sample_user.user_id, {"name": "Not Started", "status": "not_started"})
        TaskService.create_task(db_session, sample_user.user_id, {"name": "In Progress", "status": "in_progress"})
        TaskService.create_task(db_session, sample_user.user_id, {"name": "Completed", "status": "completed"})
        db_session.commit()
        
        # Filter by status
        in_progress_tasks = TaskService.get_user_tasks(
            db_session,
            sample_user.user_id,
            filters={"status": "in_progress"}
        )
        
        assert len(in_progress_tasks) == 1
        assert in_progress_tasks[0].status.value == "in_progress"
    
    def test_get_user_tasks_with_priority_filter(self, db_session, sample_user):
        """Test retrieving tasks with priority filter"""
        from src.backend.app.database.task_service import TaskService
        
        # Create tasks with different priorities
        TaskService.create_task(db_session, sample_user.user_id, {"name": "Low Priority", "priority": "low"})
        TaskService.create_task(db_session, sample_user.user_id, {"name": "High Priority 1", "priority": "high"})
        TaskService.create_task(db_session, sample_user.user_id, {"name": "High Priority 2", "priority": "high"})
        db_session.commit()
        
        # Filter by priority
        high_priority_tasks = TaskService.get_user_tasks(
            db_session,
            sample_user.user_id,
            filters={"priority": "high"}
        )
        
        assert len(high_priority_tasks) == 2
        assert all(task.priority.value == "high" for task in high_priority_tasks)
    
    def test_update_task(self, db_session, sample_task, sample_user):
        """Test task update"""
        from src.backend.app.database.task_service import TaskService
        
        updated_task = TaskService.update_task(
            db_session,
            task_id=sample_task.task_id,
            user_id=sample_user.user_id,
            updates={
                "name": "Updated Task Name",
                "status": "in_progress",
                "priority": "urgent"
            }
        )
        
        assert updated_task is not None
        assert updated_task.name == "Updated Task Name"
        assert updated_task.status.value == "in_progress"
        assert updated_task.priority.value == "urgent"
    
    def test_update_task_unauthorized(self, db_session, sample_task):
        """Test updating task with wrong user ID"""
        from src.backend.app.database.task_service import TaskService
        from uuid import uuid4
        
        # Attempt to update with different user ID
        result = TaskService.update_task(
            db_session,
            task_id=sample_task.task_id,
            user_id=uuid4(),  # Different user
            updates={"name": "Hacked"}
        )
        
        # Should fail or return None
        assert result is None or result.name != "Hacked"
    
    def test_delete_task(self, db_session, sample_task, sample_user):
        """Test task deletion"""
        from src.backend.app.database.task_service import TaskService
        
        # Delete task
        success = TaskService.delete_task(
            db_session,
            task_id=sample_task.task_id,
            user_id=sample_user.user_id
        )
        
        assert success is True
        
        # Verify task is deleted
        tasks = TaskService.get_user_tasks(db_session, sample_user.user_id)
        assert sample_task.task_id not in [task.task_id for task in tasks]
    
    def test_delete_task_unauthorized(self, db_session, sample_task):
        """Test deleting task with wrong user ID"""
        from src.backend.app.database.task_service import TaskService
        from uuid import uuid4
        
        # Attempt to delete with different user ID
        success = TaskService.delete_task(
            db_session,
            task_id=sample_task.task_id,
            user_id=uuid4()  # Different user
        )
        
        # Should fail
        assert success is False
    
    def test_get_task_by_id(self, db_session, sample_task, sample_user):
        """Test retrieving single task by ID"""
        from src.backend.app.database.task_service import TaskService
        
        task = TaskService.get_task_by_id(
            db_session,
            task_id=sample_task.task_id,
            user_id=sample_user.user_id
        )
        
        assert task is not None
        assert task.task_id == sample_task.task_id
        assert task.name == sample_task.name
    
    def test_get_overdue_tasks(self, db_session, sample_user):
        """Test retrieving overdue tasks"""
        from src.backend.app.database.task_service import TaskService
        
        # Create task with past due date
        past_date = datetime.now() - timedelta(days=1)
        TaskService.create_task(
            db_session,
            sample_user.user_id,
            {
                "name": "Overdue Task",
                "due_date": past_date.isoformat(),
                "status": "not_started"
            }
        )
        db_session.commit()
        
        # Get overdue tasks
        overdue_tasks = TaskService.get_overdue_tasks(db_session, sample_user.user_id)
        
        assert len(overdue_tasks) > 0
        assert all(task.due_date < datetime.now() for task in overdue_tasks if task.due_date)
