"""
Shared test fixtures and configuration for pytest
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/behflow_test"

from src.backend.app.database.database import Base


@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    test_db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/behflow_test")
    engine = create_engine(test_db_url, echo=False)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine):
    """Create a new database session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # Rollback and close after test
    session.rollback()
    session.close()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    from src.backend.app.database.auth_service import AuthService
    
    user = AuthService.create_user(
        db_session,
        username="testuser",
        password="password123",
        name="Test",
        lastname="User"
    )
    db_session.commit()
    return user


@pytest.fixture
def auth_token(sample_user):
    """Generate authentication token for test user"""
    from src.backend.app.database.auth_service import AuthService
    token = AuthService.generate_token(sample_user.user_id)
    return token


@pytest.fixture
def sample_task(db_session, sample_user):
    """Create a sample task for testing"""
    from src.backend.app.database.task_service import TaskService
    from uuid import UUID
    
    task = TaskService.create_task(
        db_session,
        user_id=sample_user.user_id,
        task_data={
            "name": "Sample Task",
            "description": "Sample description",
            "priority": "medium",
            "status": "not_started"
        }
    )
    db_session.commit()
    return task


@pytest.fixture
def api_client():
    """Create FastAPI test client"""
    from fastapi.testclient import TestClient
    from src.backend.app.main import app
    return TestClient(app)


# Async fixtures for agent testing
@pytest.fixture
def agent_user_id():
    """Test user ID for agent"""
    return "test-user-123"


@pytest.fixture(autouse=True)
def cleanup_agent_store():
    """Clean up agent task store after each test"""
    from src.behflow_agent.tools import _TASK_STORE, clear_current_user
    
    yield
    
    # Cleanup
    _TASK_STORE.clear()
    clear_current_user()


# Markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "e2e: marks end-to-end tests")
