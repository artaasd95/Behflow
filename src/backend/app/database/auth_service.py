"""
Authentication service - handles user authentication and authorization
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID
import bcrypt

from app.database.models import UserModel
from app.api.models.user import UserRegister, User
from shared.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def create_user(db: Session, user_data: UserRegister) -> Optional[UserModel]:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user model or None if username exists
        """
        try:
            # Hash the password
            password_hash = AuthService.hash_password(user_data.password)
            
            # Create user model
            db_user = UserModel(
                username=user_data.username,
                password_hash=password_hash,
                name=user_data.name,
                lastname=user_data.lastname
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User created: {user_data.username}")
            return db_user
            
        except IntegrityError:
            db.rollback()
            logger.warning(f"Username already exists: {user_data.username}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
        """
        Authenticate a user by username and password
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            
        Returns:
            User model if authentication successful, None otherwise
        """
        user = db.query(UserModel).filter(
            UserModel.username == username,
            UserModel.is_active == True
        ).first()
        
        if not user:
            logger.warning(f"User not found or inactive: {username}")
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        logger.info(f"User authenticated: {username}")
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserModel]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User model or None if not found
        """
        return db.query(UserModel).filter(
            UserModel.user_id == user_id,
            UserModel.is_active == True
        ).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
        """
        Get user by username
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User model or None if not found
        """
        return db.query(UserModel).filter(
            UserModel.username == username,
            UserModel.is_active == True
        ).first()
    
    @staticmethod
    def deactivate_user(db: Session, user_id: UUID) -> bool:
        """
        Deactivate a user (soft delete)
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                return False
            
            user.is_active = False
            db.commit()
            logger.info(f"User deactivated: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user: {e}")
            return False
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: UUID,
        name: Optional[str] = None,
        lastname: Optional[str] = None,
        password: Optional[str] = None
    ) -> Optional[UserModel]:
        """
        Update user information
        
        Args:
            db: Database session
            user_id: User UUID
            name: New name (optional)
            lastname: New lastname (optional)
            password: New password (optional)
            
        Returns:
            Updated user model or None if not found
        """
        try:
            user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if not user:
                return None
            
            if name is not None:
                user.name = name
            if lastname is not None:
                user.lastname = lastname
            if password is not None:
                user.password_hash = AuthService.hash_password(password)
            
            db.commit()
            db.refresh(user)
            logger.info(f"User updated: {user.username}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            raise
