"""
Tests for authentication service
"""
import pytest
from uuid import UUID


class TestAuthService:
    """Test authentication service operations"""
    
    def test_create_user(self, db_session):
        """Test user creation"""
        from src.backend.app.database.auth_service import AuthService
        
        user = AuthService.create_user(
            db_session,
            username="newuser",
            password="password123",
            name="New",
            lastname="User"
        )
        
        assert user is not None
        assert user.username == "newuser"
        assert user.name == "New"
        assert user.lastname == "User"
        assert isinstance(user.user_id, UUID)
        # Password should be hashed
        assert user.password_hash != "password123"
        assert len(user.password_hash) > 20
    
    def test_create_duplicate_user(self, db_session):
        """Test creating user with duplicate username fails"""
        from src.backend.app.database.auth_service import AuthService
        
        # Create first user
        AuthService.create_user(
            db_session,
            username="duplicate",
            password="password123",
            name="First",
            lastname="User"
        )
        db_session.commit()
        
        # Attempt to create duplicate
        with pytest.raises(Exception):  # Should raise integrity error
            AuthService.create_user(
                db_session,
                username="duplicate",  # Same username
                password="password456",
                name="Second",
                lastname="User"
            )
            db_session.commit()
    
    def test_authenticate_success(self, db_session):
        """Test successful authentication"""
        from src.backend.app.database.auth_service import AuthService
        
        # Create user
        created_user = AuthService.create_user(
            db_session,
            username="authuser",
            password="correctpassword",
            name="Auth",
            lastname="User"
        )
        db_session.commit()
        
        # Authenticate with correct credentials
        authenticated_user = AuthService.authenticate(
            db_session,
            username="authuser",
            password="correctpassword"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.user_id == created_user.user_id
        assert authenticated_user.username == "authuser"
    
    def test_authenticate_wrong_password(self, db_session):
        """Test authentication with wrong password"""
        from src.backend.app.database.auth_service import AuthService
        
        # Create user
        AuthService.create_user(
            db_session,
            username="authuser",
            password="correctpassword",
            name="Auth",
            lastname="User"
        )
        db_session.commit()
        
        # Attempt authentication with wrong password
        authenticated_user = AuthService.authenticate(
            db_session,
            username="authuser",
            password="wrongpassword"
        )
        
        assert authenticated_user is None
    
    def test_authenticate_nonexistent_user(self, db_session):
        """Test authentication with nonexistent username"""
        from src.backend.app.database.auth_service import AuthService
        
        authenticated_user = AuthService.authenticate(
            db_session,
            username="nonexistent",
            password="password123"
        )
        
        assert authenticated_user is None
    
    def test_get_user_by_id(self, db_session):
        """Test retrieving user by ID"""
        from src.backend.app.database.auth_service import AuthService
        
        # Create user
        created_user = AuthService.create_user(
            db_session,
            username="getuser",
            password="password123",
            name="Get",
            lastname="User"
        )
        db_session.commit()
        
        # Retrieve user by ID
        retrieved_user = AuthService.get_user_by_id(db_session, created_user.user_id)
        
        assert retrieved_user is not None
        assert retrieved_user.user_id == created_user.user_id
        assert retrieved_user.username == "getuser"
    
    def test_get_user_by_nonexistent_id(self, db_session):
        """Test retrieving user with nonexistent ID"""
        from src.backend.app.database.auth_service import AuthService
        from uuid import uuid4
        
        fake_id = uuid4()
        user = AuthService.get_user_by_id(db_session, fake_id)
        
        assert user is None
    
    def test_generate_token(self, sample_user):
        """Test JWT token generation"""
        from src.backend.app.database.auth_service import AuthService
        
        token = AuthService.generate_token(sample_user.user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
    
    def test_verify_token(self, sample_user):
        """Test JWT token verification"""
        from src.backend.app.database.auth_service import AuthService
        
        # Generate token
        token = AuthService.generate_token(sample_user.user_id)
        
        # Verify token
        user_id = AuthService.verify_token(token)
        
        assert user_id is not None
        assert user_id == sample_user.user_id
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        from src.backend.app.database.auth_service import AuthService
        
        invalid_token = "invalid.token.here"
        user_id = AuthService.verify_token(invalid_token)
        
        assert user_id is None
