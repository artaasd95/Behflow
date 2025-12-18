"""
SQLAlchemy database models for Behflow
"""
from sqlalchemy import Column, String, DateTime, Text, Enum, ARRAY, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database.database import Base


class PriorityEnum(str, enum.Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StatusEnum(str, enum.Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserModel(Base):
    """User database model"""
    __tablename__ = "users"

    user_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    tasks = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSessionModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


class TaskModel(Base):
    """Task database model"""
    __tablename__ = "tasks"

    task_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Task details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Dates - Gregorian
    due_date_gregorian = Column(DateTime(timezone=True), nullable=True)
    date_added_gregorian = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Dates - Jalali
    due_date_jalali = Column(String(50), nullable=True)
    date_added_jalali = Column(String(50), nullable=False)
    
    # Task properties
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False, index=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Metadata
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="tasks")

    def __repr__(self):
        return f"<Task(task_id={self.task_id}, name={self.name}, status={self.status})>"


class ChatSessionModel(Base):
    """Chat session database model"""
    __tablename__ = "chat_sessions"

    session_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session details
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="chat_sessions")
    messages = relationship("ChatMessageModel", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(session_id={self.session_id}, user_id={self.user_id})>"


class ChatMessageModel(Base):
    """Chat message database model"""
    __tablename__ = "chat_messages"

    message_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    
    # Relationships
    session = relationship("ChatSessionModel", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(message_id={self.message_id}, role={self.role})>"
