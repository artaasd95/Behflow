"""
Automated Process Service - handles automated process operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.database.models import (
    AutomatedProcessModel,
    AutomatedProcessExecutionModel,
    TriggerTypeEnum,
    ProcessStatusEnum
)
from shared.logger import get_logger

logger = get_logger(__name__)


class AutomatedProcessService:
    """Service class for automated process operations"""
    
    @staticmethod
    def create_process(
        db: Session,
        name: str,
        description: Optional[str],
        trigger_type: TriggerTypeEnum,
        schedule_config: Optional[Dict[str, Any]] = None,
        process_config: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True
    ) -> AutomatedProcessModel:
        """
        Create a new automated process
        
        Args:
            db: Database session
            name: Process name (unique)
            description: Process description
            trigger_type: Type of trigger (manual, time_based, event_based)
            schedule_config: Schedule configuration for time-based triggers
            process_config: Process-specific configuration
            is_enabled: Whether the process is enabled
            
        Returns:
            Created process model
        """
        try:
            db_process = AutomatedProcessModel(
                name=name,
                description=description,
                trigger_type=trigger_type,
                schedule_config=schedule_config,
                process_config=process_config,
                is_enabled=is_enabled
            )
            
            db.add(db_process)
            db.commit()
            db.refresh(db_process)
            
            logger.info(f"Automated process created: {name}")
            return db_process
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating automated process: {e}")
            raise
    
    @staticmethod
    def get_process_by_id(db: Session, process_id: UUID) -> Optional[AutomatedProcessModel]:
        """Get process by ID"""
        return db.query(AutomatedProcessModel).filter(
            AutomatedProcessModel.process_id == process_id
        ).first()
    
    @staticmethod
    def get_process_by_name(db: Session, name: str) -> Optional[AutomatedProcessModel]:
        """Get process by name"""
        return db.query(AutomatedProcessModel).filter(
            AutomatedProcessModel.name == name
        ).first()
    
    @staticmethod
    def get_all_processes(db: Session, enabled_only: bool = False) -> List[AutomatedProcessModel]:
        """
        Get all automated processes
        
        Args:
            db: Database session
            enabled_only: If True, only return enabled processes
            
        Returns:
            List of process models
        """
        query = db.query(AutomatedProcessModel)
        if enabled_only:
            query = query.filter(AutomatedProcessModel.is_enabled == True)
        return query.all()
    
    @staticmethod
    def get_processes_by_trigger_type(
        db: Session,
        trigger_type: TriggerTypeEnum,
        enabled_only: bool = True
    ) -> List[AutomatedProcessModel]:
        """
        Get processes by trigger type
        
        Args:
            db: Database session
            trigger_type: Type of trigger to filter by
            enabled_only: If True, only return enabled processes
            
        Returns:
            List of process models
        """
        # Use .value to get the string value of the enum for proper comparison
        trigger_value = trigger_type.value if isinstance(trigger_type, TriggerTypeEnum) else trigger_type
        query = db.query(AutomatedProcessModel).filter(
            AutomatedProcessModel.trigger_type == trigger_value
        )
        if enabled_only:
            query = query.filter(AutomatedProcessModel.is_enabled == True)
        return query.all()
    
    @staticmethod
    def update_process(
        db: Session,
        process_id: UUID,
        **kwargs
    ) -> Optional[AutomatedProcessModel]:
        """
        Update process information
        
        Args:
            db: Database session
            process_id: Process UUID
            **kwargs: Fields to update
            
        Returns:
            Updated process model or None if not found
        """
        try:
            process = db.query(AutomatedProcessModel).filter(
                AutomatedProcessModel.process_id == process_id
            ).first()
            
            if not process:
                return None
            
            for key, value in kwargs.items():
                if hasattr(process, key) and value is not None:
                    setattr(process, key, value)
            
            db.commit()
            db.refresh(process)
            logger.info(f"Automated process updated: {process.name}")
            return process
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating automated process: {e}")
            raise
    
    @staticmethod
    def update_last_executed(db: Session, process_id: UUID) -> None:
        """Update the last executed timestamp"""
        try:
            process = db.query(AutomatedProcessModel).filter(
                AutomatedProcessModel.process_id == process_id
            ).first()
            
            if process:
                process.last_executed_at = datetime.now(timezone.utc)
                db.commit()
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating last executed timestamp: {e}")
    
    @staticmethod
    def create_execution(
        db: Session,
        process_id: UUID,
        status: ProcessStatusEnum = ProcessStatusEnum.PENDING
    ) -> AutomatedProcessExecutionModel:
        """
        Create a new execution record
        
        Args:
            db: Database session
            process_id: Process UUID
            status: Initial status
            
        Returns:
            Created execution model
        """
        try:
            execution = AutomatedProcessExecutionModel(
                process_id=process_id,
                status=status,
                started_at=datetime.now(timezone.utc) if status == ProcessStatusEnum.RUNNING else None
            )
            
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            return execution
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating execution record: {e}")
            raise
    
    @staticmethod
    def update_execution(
        db: Session,
        execution_id: UUID,
        status: Optional[ProcessStatusEnum] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[AutomatedProcessExecutionModel]:
        """
        Update execution record
        
        Args:
            db: Database session
            execution_id: Execution UUID
            status: New status
            result: Execution result
            error_message: Error message if failed
            
        Returns:
            Updated execution model or None if not found
        """
        try:
            execution = db.query(AutomatedProcessExecutionModel).filter(
                AutomatedProcessExecutionModel.execution_id == execution_id
            ).first()
            
            if not execution:
                return None
            
            if status:
                execution.status = status
                if status == ProcessStatusEnum.RUNNING and not execution.started_at:
                    execution.started_at = datetime.now(timezone.utc)
                elif status in [ProcessStatusEnum.COMPLETED, ProcessStatusEnum.FAILED]:
                    execution.completed_at = datetime.now(timezone.utc)
            
            if result is not None:
                execution.result = result
            
            if error_message is not None:
                execution.error_message = error_message
            
            db.commit()
            db.refresh(execution)
            
            return execution
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating execution record: {e}")
            raise
    
    @staticmethod
    def get_execution_history(
        db: Session,
        process_id: UUID,
        limit: int = 50
    ) -> List[AutomatedProcessExecutionModel]:
        """
        Get execution history for a process
        
        Args:
            db: Database session
            process_id: Process UUID
            limit: Maximum number of records to return
            
        Returns:
            List of execution models
        """
        return db.query(AutomatedProcessExecutionModel).filter(
            AutomatedProcessExecutionModel.process_id == process_id
        ).order_by(
            AutomatedProcessExecutionModel.started_at.desc()
        ).limit(limit).all()
