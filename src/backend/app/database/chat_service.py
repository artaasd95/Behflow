"""
Chat service - handles chat session and message operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.database.models import ChatSessionModel, ChatMessageModel
from shared.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service class for chat operations"""
    
    @staticmethod
    def create_session(
        db: Session,
        user_id: UUID,
        title: Optional[str] = None
    ) -> ChatSessionModel:
        """
        Create a new chat session
        
        Args:
            db: Database session
            user_id: User UUID
            title: Session title (optional)
            
        Returns:
            Created chat session model
        """
        try:
            db_session = ChatSessionModel(
                user_id=user_id,
                title=title or f"Chat {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
            )
            
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            logger.info(f"Chat session created: {db_session.session_id} for user {user_id}")
            return db_session
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating chat session: {e}")
            raise
    
    @staticmethod
    def get_session_by_id(db: Session, session_id: UUID) -> Optional[ChatSessionModel]:
        """
        Get chat session by ID
        
        Args:
            db: Database session
            session_id: Session UUID
            
        Returns:
            Chat session model or None if not found
        """
        return db.query(ChatSessionModel).filter(
            ChatSessionModel.session_id == session_id
        ).first()
    
    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: UUID,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSessionModel]:
        """
        Get chat sessions for a specific user
        
        Args:
            db: Database session
            user_id: User UUID
            active_only: Only return active sessions
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of chat session models
        """
        query = db.query(ChatSessionModel).filter(ChatSessionModel.user_id == user_id)
        
        if active_only:
            query = query.filter(ChatSessionModel.is_active == True)
        
        return query.order_by(ChatSessionModel.updated_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_session_title(
        db: Session,
        session_id: UUID,
        title: str
    ) -> Optional[ChatSessionModel]:
        """
        Update chat session title
        
        Args:
            db: Database session
            session_id: Session UUID
            title: New title
            
        Returns:
            Updated chat session model or None if not found
        """
        try:
            session = db.query(ChatSessionModel).filter(
                ChatSessionModel.session_id == session_id
            ).first()
            
            if not session:
                return None
            
            session.title = title
            db.commit()
            db.refresh(session)
            logger.info(f"Session title updated: {session_id}")
            return session
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating session title: {e}")
            raise
    
    @staticmethod
    def deactivate_session(db: Session, session_id: UUID) -> bool:
        """
        Deactivate a chat session (soft delete)
        
        Args:
            db: Database session
            session_id: Session UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db.query(ChatSessionModel).filter(
                ChatSessionModel.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            session.is_active = False
            db.commit()
            logger.info(f"Session deactivated: {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating session: {e}")
            return False
    
    @staticmethod
    def delete_session(db: Session, session_id: UUID) -> bool:
        """
        Delete a chat session (hard delete)
        
        Args:
            db: Database session
            session_id: Session UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db.query(ChatSessionModel).filter(
                ChatSessionModel.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            db.delete(session)
            db.commit()
            logger.info(f"Session deleted: {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting session: {e}")
            return False
    
    @staticmethod
    def add_message(
        db: Session,
        session_id: UUID,
        role: str,
        content: str,
        tokens_used: Optional[int] = None
    ) -> ChatMessageModel:
        """
        Add a message to a chat session
        
        Args:
            db: Database session
            session_id: Session UUID
            role: Message role ('user' or 'assistant')
            content: Message content
            tokens_used: Number of tokens used (optional)
            
        Returns:
            Created chat message model
        """
        try:
            db_message = ChatMessageModel(
                session_id=session_id,
                role=role,
                content=content,
                tokens_used=tokens_used
            )
            
            db.add(db_message)
            
            # Update session's updated_at timestamp
            session = db.query(ChatSessionModel).filter(
                ChatSessionModel.session_id == session_id
            ).first()
            if session:
                session.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(db_message)
            
            logger.debug(f"Message added to session {session_id}")
            return db_message
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding message: {e}")
            raise
    
    @staticmethod
    def get_session_messages(
        db: Session,
        session_id: UUID,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatMessageModel]:
        """
        Get messages for a chat session
        
        Args:
            db: Database session
            session_id: Session UUID
            limit: Maximum number of messages to return (optional)
            offset: Number of messages to skip
            
        Returns:
            List of chat message models
        """
        query = db.query(ChatMessageModel).filter(
            ChatMessageModel.session_id == session_id
        ).order_by(ChatMessageModel.created_at.asc()).offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_message_by_id(db: Session, message_id: UUID) -> Optional[ChatMessageModel]:
        """
        Get message by ID
        
        Args:
            db: Database session
            message_id: Message UUID
            
        Returns:
            Chat message model or None if not found
        """
        return db.query(ChatMessageModel).filter(
            ChatMessageModel.message_id == message_id
        ).first()
    
    @staticmethod
    def delete_message(db: Session, message_id: UUID) -> bool:
        """
        Delete a chat message
        
        Args:
            db: Database session
            message_id: Message UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            message = db.query(ChatMessageModel).filter(
                ChatMessageModel.message_id == message_id
            ).first()
            
            if not message:
                return False
            
            db.delete(message)
            db.commit()
            logger.info(f"Message deleted: {message_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting message: {e}")
            return False
    
    @staticmethod
    def get_session_token_usage(db: Session, session_id: UUID) -> dict:
        """
        Get token usage statistics for a session
        
        Args:
            db: Database session
            session_id: Session UUID
            
        Returns:
            Dictionary with token usage statistics
        """
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.session_id == session_id
        ).all()
        
        total_tokens = sum(msg.tokens_used or 0 for msg in messages)
        message_count = len(messages)
        
        return {
            "total_tokens": total_tokens,
            "message_count": message_count,
            "avg_tokens_per_message": total_tokens / message_count if message_count > 0 else 0
        }
