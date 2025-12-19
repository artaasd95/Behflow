"""
Tasks router - handles task-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session

from app.api.routers.auth import get_current_user_from_header
from app.api.models.user import User
from app.database.database import get_db
from app.database.task_service import TaskService
from app.database.models import StatusEnum, PriorityEnum
from shared.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["tasks"])


class UpdateTaskStatusRequest(BaseModel):
    """Request model for updating task status"""
    task_id: UUID
    status: StatusEnum


class UpdateTaskStatusResponse(BaseModel):
    """Response model for task status update"""
    success: bool
    message: str
    task_id: UUID
    new_status: str


class TaskResponse(BaseModel):
    """Response model for task data"""
    task_id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    due_date_gregorian: Optional[str]
    due_date_jalali: Optional[str]
    date_added_gregorian: str
    date_added_jalali: str
    priority: str
    status: str
    tags: Optional[List[str]]


@router.put("/tasks/status", response_model=UpdateTaskStatusResponse)
async def update_task_status(
    request: UpdateTaskStatusRequest,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
) -> UpdateTaskStatusResponse:
    """
    Update the status of a task
    
    Args:
        request: Contains task_id and new status
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success status and updated task info
    """
    logger.info(f"Status update request for task {request.task_id} by user {current_user.username}")
    
    try:
        # Get the task
        task = TaskService.get_task_by_id(db, request.task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {request.task_id} not found"
            )
        
        # Verify the task belongs to the current user
        if task.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this task"
            )
        
        # Update the task status
        updated_task = TaskService.update_task(
            db=db,
            task_id=request.task_id,
            status=request.status
        )
        
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task status"
            )
        
        logger.info(f"Task {request.task_id} status updated to {request.status}")
        
        return UpdateTaskStatusResponse(
            success=True,
            message=f"Task status updated to {request.status.value}",
            task_id=request.task_id,
            new_status=request.status.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/tasks/{task_id}/complete", response_model=UpdateTaskStatusResponse)
async def mark_task_complete(
    task_id: UUID,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
) -> UpdateTaskStatusResponse:
    """
    Mark a task as completed (convenience endpoint)
    
    Args:
        task_id: UUID of the task
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success status and updated task info
    """
    logger.info(f"Complete task request for {task_id} by user {current_user.username}")
    
    request = UpdateTaskStatusRequest(
        task_id=task_id,
        status=StatusEnum.COMPLETED
    )
    
    return await update_task_status(request, current_user, db)


@router.get("/tasks", response_model=List[TaskResponse])
async def get_user_tasks(
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db),
    status_filter: Optional[StatusEnum] = None,
    priority_filter: Optional[PriorityEnum] = None,
    limit: int = 100,
    offset: int = 0
) -> List[TaskResponse]:
    """
    Get all tasks for the current user
    
    Args:
        current_user: Authenticated user
        db: Database session
        status_filter: Optional status filter
        priority_filter: Optional priority filter
        limit: Maximum number of tasks
        offset: Pagination offset
        
    Returns:
        List of tasks
    """
    logger.info(f"Get tasks request for user {current_user.username}")
    
    try:
        tasks = TaskService.get_user_tasks(
            db=db,
            user_id=current_user.user_id,
            status=status_filter,
            priority=priority_filter,
            limit=limit,
            offset=offset
        )
        
        return [
            TaskResponse(
                task_id=task.task_id,
                user_id=task.user_id,
                name=task.name,
                description=task.description,
                due_date_gregorian=task.due_date_gregorian.isoformat() if task.due_date_gregorian else None,
                due_date_jalali=task.due_date_jalali,
                date_added_gregorian=task.date_added_gregorian.isoformat(),
                date_added_jalali=task.date_added_jalali,
                priority=task.priority.value,
                status=task.status.value,
                tags=task.tags
            )
            for task in tasks
        ]
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
