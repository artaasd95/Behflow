"""
Task service - handles task CRUD operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.models import TaskModel, PriorityEnum, StatusEnum
from behflow_agent.models.task import Task
from shared.logger import get_logger

logger = get_logger(__name__)


class TaskService:
    """Service class for task operations"""
    
    @staticmethod
    def create_task(db: Session, task: Task) -> TaskModel:
        """
        Create a new task
        
        Args:
            db: Database session
            task: Task pydantic model
            
        Returns:
            Created task model
        """
        try:
            db_task = TaskModel(
                task_id=task.task_id,
                user_id=task.user_id,
                name=task.name,
                description=task.description,
                due_date_gregorian=task.due_date_gregorian,
                due_date_jalali=task.due_date_jalali,
                date_added_gregorian=task.date_added_gregorian,
                date_added_jalali=task.date_added_jalali,
                priority=PriorityEnum[task.priority.upper()],
                status=StatusEnum[task.status.upper()],
                tags=task.tags
            )
            
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            
            logger.info(f"Task created: {task.name} for user {task.user_id}")
            return db_task
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating task: {e}")
            raise
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: UUID) -> Optional[TaskModel]:
        """
        Get task by ID
        
        Args:
            db: Database session
            task_id: Task UUID
            
        Returns:
            Task model or None if not found
        """
        return db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    
    @staticmethod
    def get_user_tasks(
        db: Session,
        user_id: UUID,
        status: Optional[StatusEnum] = None,
        priority: Optional[PriorityEnum] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskModel]:
        """
        Get tasks for a specific user with optional filters
        
        Args:
            db: Database session
            user_id: User UUID
            status: Filter by status (optional)
            priority: Filter by priority (optional)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            
        Returns:
            List of task models
        """
        query = db.query(TaskModel).filter(TaskModel.user_id == user_id)
        
        if status:
            query = query.filter(TaskModel.status == status)
        if priority:
            query = query.filter(TaskModel.priority == priority)
        
        return query.order_by(TaskModel.date_added_gregorian.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        due_date_gregorian: Optional[datetime] = None,
        due_date_jalali: Optional[str] = None,
        priority: Optional[PriorityEnum] = None,
        status: Optional[StatusEnum] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[TaskModel]:
        """
        Update task information
        
        Args:
            db: Database session
            task_id: Task UUID
            name: New name (optional)
            description: New description (optional)
            due_date_gregorian: New due date gregorian (optional)
            due_date_jalali: New due date jalali (optional)
            priority: New priority (optional)
            status: New status (optional)
            tags: New tags (optional)
            
        Returns:
            Updated task model or None if not found
        """
        try:
            task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
            if not task:
                return None
            
            if name is not None:
                task.name = name
            if description is not None:
                task.description = description
            if due_date_gregorian is not None:
                task.due_date_gregorian = due_date_gregorian
            if due_date_jalali is not None:
                task.due_date_jalali = due_date_jalali
            if priority is not None:
                task.priority = priority
            if status is not None:
                task.status = status
                # Mark as completed if status is COMPLETED
                if status == StatusEnum.COMPLETED and not task.completed_at:
                    task.completed_at = datetime.utcnow()
            if tags is not None:
                task.tags = tags
            
            db.commit()
            db.refresh(task)
            logger.info(f"Task updated: {task.name}")
            return task
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating task: {e}")
            raise
    
    @staticmethod
    def delete_task(db: Session, task_id: UUID) -> bool:
        """
        Delete a task
        
        Args:
            db: Database session
            task_id: Task UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
            if not task:
                return False
            
            db.delete(task)
            db.commit()
            logger.info(f"Task deleted: {task_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting task: {e}")
            return False
    
    @staticmethod
    def search_tasks(
        db: Session,
        user_id: UUID,
        search_term: str,
        limit: int = 50
    ) -> List[TaskModel]:
        """
        Search tasks by name or description
        
        Args:
            db: Database session
            user_id: User UUID
            search_term: Search term
            limit: Maximum number of tasks to return
            
        Returns:
            List of task models
        """
        search_pattern = f"%{search_term}%"
        return db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            or_(
                TaskModel.name.ilike(search_pattern),
                TaskModel.description.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_tasks_by_tag(
        db: Session,
        user_id: UUID,
        tag: str,
        limit: int = 100
    ) -> List[TaskModel]:
        """
        Get tasks by tag
        
        Args:
            db: Database session
            user_id: User UUID
            tag: Tag to filter by
            limit: Maximum number of tasks to return
            
        Returns:
            List of task models
        """
        return db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.tags.contains([tag])
        ).limit(limit).all()
    
    @staticmethod
    def get_overdue_tasks(db: Session, user_id: UUID) -> List[TaskModel]:
        """
        Get overdue tasks for a user
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            List of overdue task models
        """
        now = datetime.utcnow()
        return db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.due_date_gregorian < now,
            TaskModel.status.in_([StatusEnum.PENDING, StatusEnum.IN_PROGRESS])
        ).order_by(TaskModel.due_date_gregorian).all()
    
    @staticmethod
    def get_task_statistics(db: Session, user_id: UUID) -> dict:
        """
        Get task statistics for a user
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Dictionary with task statistics
        """
        total = db.query(TaskModel).filter(TaskModel.user_id == user_id).count()
        pending = db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.status == StatusEnum.PENDING
        ).count()
        in_progress = db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.status == StatusEnum.IN_PROGRESS
        ).count()
        completed = db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.status == StatusEnum.COMPLETED
        ).count()
        cancelled = db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.status == StatusEnum.CANCELLED
        ).count()
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled
        }
