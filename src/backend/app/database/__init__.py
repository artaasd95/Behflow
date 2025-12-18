"""
Database module - provides database configuration, models, and services
"""
from app.database.database import (
    Base,
    engine,
    SessionLocal,
    get_db,
    init_db,
    drop_db,
    reset_db
)
from app.database.models import (
    UserModel,
    TaskModel,
    ChatSessionModel,
    ChatMessageModel,
    PriorityEnum,
    StatusEnum
)
from app.database.auth_service import AuthService
from app.database.task_service import TaskService
from app.database.chat_service import ChatService

__all__ = [
    # Database
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "drop_db",
    "reset_db",
    # Models
    "UserModel",
    "TaskModel",
    "ChatSessionModel",
    "ChatMessageModel",
    "PriorityEnum",
    "StatusEnum",
    # Services
    "AuthService",
    "TaskService",
    "ChatService",
]
