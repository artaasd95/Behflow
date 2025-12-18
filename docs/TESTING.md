# Testing Guide

## Overview

Behflow uses a comprehensive testing strategy covering unit tests, integration tests, and end-to-end tests. This guide explains testing practices, tools, and how to run tests.

## Testing Strategy

### Test Pyramid

```
        /\
       /  \
      / E2E \      ← Few, expensive, slow
     /------\
    /  Inte- \    ← Some, moderate cost
   /  gration \
  /------------\
 /  Unit Tests  \ ← Many, cheap, fast
/________________\
```

- **Unit Tests (70%)**: Test individual functions and classes
- **Integration Tests (20%)**: Test component interactions
- **End-to-End Tests (10%)**: Test complete user workflows

## Technology Stack

| Component | Framework | Purpose |
|-----------|-----------|---------|
| Backend | pytest | Unit & integration tests |
| Frontend | Jest + Testing Library | JavaScript tests |
| Agent | pytest + pytest-asyncio | Async agent tests |
| API | httpx + TestClient | API endpoint tests |
| Database | pytest-postgresql | Database tests |
| Mocking | unittest.mock + pytest-mock | Mock dependencies |

## Backend Testing

### Setup

```bash
# Install test dependencies
cd src/backend
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_service.py

# Run specific test
pytest tests/test_auth_service.py::test_create_user

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── backend/
│   ├── __init__.py
│   ├── test_auth_service.py
│   ├── test_task_service.py
│   ├── test_chat_service.py
│   ├── test_automated_process_service.py
│   └── test_api_endpoints.py
├── agent/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_builder.py
└── integration/
    ├── __init__.py
    ├── test_task_workflow.py
    └── test_chat_workflow.py
```

### Example Unit Tests

```python
# tests/backend/test_auth_service.py

import pytest
from uuid import uuid4
from app.database.auth_service import AuthService
from app.database.models import UserModel

def test_create_user(db_session):
    """Test user creation"""
    user = AuthService.create_user(
        db_session,
        username="testuser",
        password="password123",
        name="Test",
        lastname="User"
    )
    
    assert user.username == "testuser"
    assert user.name == "Test"
    assert user.lastname == "User"
    assert user.user_id is not None
    assert user.password_hash != "password123"  # Should be hashed

def test_create_duplicate_user(db_session):
    """Test duplicate username error"""
    AuthService.create_user(
        db_session,
        username="testuser",
        password="password123",
        name="Test",
        lastname="User"
    )
    
    with pytest.raises(ValueError, match="Username already exists"):
        AuthService.create_user(
            db_session,
            username="testuser",  # Duplicate
            password="password456",
            name="Test2",
            lastname="User2"
        )

def test_authenticate_success(db_session):
    """Test successful authentication"""
    # Create user
    AuthService.create_user(
        db_session,
        username="testuser",
        password="password123",
        name="Test",
        lastname="User"
    )
    
    # Authenticate
    user = AuthService.authenticate(
        db_session,
        username="testuser",
        password="password123"
    )
    
    assert user is not None
    assert user.username == "testuser"

def test_authenticate_failure(db_session):
    """Test failed authentication"""
    # Create user
    AuthService.create_user(
        db_session,
        username="testuser",
        password="password123",
        name="Test",
        lastname="User"
    )
    
    # Wrong password
    user = AuthService.authenticate(
        db_session,
        username="testuser",
        password="wrongpassword"
    )
    
    assert user is None
```

### API Endpoint Tests

```python
# tests/backend/test_api_endpoints.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_register_endpoint():
    """Test user registration"""
    response = client.post("/register", json={
        "username": "newuser",
        "password": "password123",
        "name": "New",
        "lastname": "User"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "user_id" in data

def test_login_endpoint():
    """Test login"""
    # Register user first
    client.post("/register", json={
        "username": "testuser",
        "password": "password123",
        "name": "Test",
        "lastname": "User"
    })
    
    # Login
    response = client.post("/login", json={
        "username": "testuser",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data

def test_create_task_endpoint(auth_token):
    """Test task creation"""
    response = client.post(
        "/api/v1/tasks",
        headers={"Authorization": auth_token},
        json={
            "name": "Test Task",
            "description": "Test description",
            "priority": "high"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["priority"] == "high"

def test_unauthorized_access():
    """Test unauthorized API access"""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401
```

### Fixtures

```python
# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.main import app

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/behflow_test")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine):
    """Create database session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def auth_token(db_session):
    """Create authenticated user and return token"""
    from app.database.auth_service import AuthService
    
    user = AuthService.create_user(
        db_session,
        username="testuser",
        password="password123",
        name="Test",
        lastname="User"
    )
    
    # Generate token
    token = AuthService.generate_token(user.user_id)
    return token

@pytest.fixture
def sample_task(db_session, auth_token):
    """Create sample task for testing"""
    from app.database.task_service import TaskService
    
    task = TaskService.create_task(
        db_session,
        user_id=extract_user_id(auth_token),
        task_data={
            "name": "Sample Task",
            "description": "Sample description",
            "priority": "medium"
        }
    )
    return task
```

## Agent Testing

### Async Tests

```python
# tests/agent/test_agent.py

import pytest
from behflow_agent.builder import AgentBuilder
from behflow_agent.tools import set_current_user, clear_current_user

@pytest.mark.asyncio
async def test_agent_invocation():
    """Test basic agent invocation"""
    agent = AgentBuilder.build(user_id="test-user-123")
    
    response = await agent.ainvoke(
        "Create a task called 'Test Task' with high priority"
    )
    
    assert "messages" in response
    assert len(response["messages"]) > 0
    assert "Test Task" in str(response["messages"][-1].content)

@pytest.mark.asyncio
async def test_agent_context_management():
    """Test agent user context"""
    set_current_user("test-user-123")
    
    from behflow_agent.tools import add_task
    result = add_task.invoke({
        "name": "Context Test",
        "priority": "medium"
    })
    
    assert "created successfully" in result
    clear_current_user()
```

### Tool Tests

```python
# tests/agent/test_tools.py

import pytest
from uuid import UUID
from behflow_agent.tools import (
    add_task, update_task, list_tasks, delete_task,
    set_current_user, clear_current_user, _TASK_STORE
)

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and cleanup for each test"""
    set_current_user("test-user-123")
    yield
    clear_current_user()
    _TASK_STORE.clear()

def test_add_task():
    """Test task creation tool"""
    result = add_task.invoke({
        "name": "Test Task",
        "description": "Test description",
        "priority": "high",
        "tags": ["test", "urgent"]
    })
    
    assert "created successfully" in result
    assert "Test Task" in result
    assert len(_TASK_STORE) == 1

def test_list_tasks():
    """Test task listing tool"""
    # Create some tasks
    add_task.invoke({"name": "Task 1", "priority": "high"})
    add_task.invoke({"name": "Task 2", "priority": "low"})
    
    # List all
    result = list_tasks.invoke({})
    assert "Found 2 tasks" in result
    assert "Task 1" in result
    assert "Task 2" in result

def test_update_task():
    """Test task update tool"""
    # Create task
    result = add_task.invoke({"name": "Original Name"})
    task_id = extract_task_id(result)
    
    # Update task
    result = update_task.invoke({
        "task_id": str(task_id),
        "name": "Updated Name",
        "status": "in_progress"
    })
    
    assert "updated successfully" in result
    assert "Updated Name" in result

def test_delete_task():
    """Test task deletion tool"""
    # Create task
    result = add_task.invoke({"name": "To Delete"})
    task_id = extract_task_id(result)
    
    # Delete task
    result = delete_task.invoke({"task_id": str(task_id)})
    assert "deleted successfully" in result
    assert len(_TASK_STORE) == 0
```

## Frontend Testing

### Setup

```bash
cd src/frontend
npm install --save-dev jest @testing-library/dom @testing-library/jest-dom

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### JavaScript Tests

```javascript
// tests/frontend/app.test.js

import { JSDOM } from 'jsdom';
import { createTaskElement, renderTasks } from '../app.js';

describe('Task Management', () => {
  let dom;
  let document;

  beforeEach(() => {
    dom = new JSDOM('<!DOCTYPE html><div id="app"></div>');
    document = dom.window.document;
    global.document = document;
  });

  test('createTaskElement creates task card', () => {
    const task = {
      task_id: '123',
      name: 'Test Task',
      description: 'Test description',
      priority: 'high',
      status: 'not_started'
    };

    const element = createTaskElement(task);
    
    expect(element.tagName).toBe('DIV');
    expect(element.className).toContain('task-card');
    expect(element.textContent).toContain('Test Task');
  });

  test('renderTasks groups tasks by status', () => {
    const tasks = [
      { task_id: '1', name: 'Task 1', status: 'not_started', priority: 'high' },
      { task_id: '2', name: 'Task 2', status: 'in_progress', priority: 'medium' },
      { task_id: '3', name: 'Task 3', status: 'completed', priority: 'low' }
    ];

    renderTasks(tasks);

    const notStarted = document.getElementById('notStartedTasks');
    const inProgress = document.getElementById('inProgressTasks');
    const completed = document.getElementById('completedTasks');

    expect(notStarted.children.length).toBe(1);
    expect(inProgress.children.length).toBe(1);
    expect(completed.children.length).toBe(1);
  });
});

describe('Authentication', () => {
  test('stores token on successful login', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ token: 'test-token', user: { username: 'test' } })
    });
    global.fetch = mockFetch;

    await loginUser('testuser', 'password123');

    expect(localStorage.getItem('token')).toBe('test-token');
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/login'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});
```

## Integration Tests

### Task Workflow Test

```python
# tests/integration/test_task_workflow.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_complete_task_workflow():
    """Test complete task creation and management workflow"""
    
    # 1. Register user
    register_response = client.post("/register", json={
        "username": "taskuser",
        "password": "password123",
        "name": "Task",
        "lastname": "User"
    })
    assert register_response.status_code == 200
    
    # 2. Login
    login_response = client.post("/login", json={
        "username": "taskuser",
        "password": "password123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    
    # 3. Create task via chat
    chat_response = client.post(
        "/api/v1/chat",
        headers={"Authorization": token},
        json={"message": "Create a task called 'Integration Test Task' with high priority"}
    )
    assert chat_response.status_code == 200
    
    # 4. List tasks
    tasks_response = client.get(
        "/api/v1/tasks",
        headers={"Authorization": token}
    )
    assert tasks_response.status_code == 200
    tasks = tasks_response.json()["tasks"]
    assert len(tasks) > 0
    assert any("Integration Test Task" in task["name"] for task in tasks)
    
    # 5. Update task
    task_id = tasks[0]["task_id"]
    update_response = client.put(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": token},
        json={"status": "completed"}
    )
    assert update_response.status_code == 200
    
    # 6. Delete task
    delete_response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": token}
    )
    assert delete_response.status_code == 204
```

## Test Coverage

### Measuring Coverage

```bash
# Backend coverage
pytest --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Coverage goals
# - Overall: > 80%
# - Critical paths: > 90%
# - Utilities: > 70%
```

### Coverage Report Example

```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
app/__init__.py                         2      0   100%
app/main.py                            45      3    93%
app/database/auth_service.py           78      5    94%
app/database/task_service.py          102      8    92%
app/database/chat_service.py           65      7    89%
app/api/routers/auth.py                34      2    94%
app/api/routers/chat.py                28      4    86%
--------------------------------------------------------
TOTAL                                 354     29    92%
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: behflow_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/behflow_test
        run: |
          cd src/backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd src/frontend
          npm install
      
      - name: Run tests
        run: |
          cd src/frontend
          npm test -- --coverage
```

## Best Practices

### Writing Good Tests

1. **Arrange, Act, Assert**: Structure tests clearly
2. **Test One Thing**: Each test should verify one behavior
3. **Use Descriptive Names**: `test_create_user_with_duplicate_username`
4. **Independent Tests**: No test dependencies
5. **Fast Tests**: Unit tests should run in milliseconds
6. **Mock External Dependencies**: Don't call real APIs in tests
7. **Test Edge Cases**: Null values, empty lists, invalid input

### Mocking

```python
from unittest.mock import patch, Mock

@patch('app.database.auth_service.hash_password')
def test_with_mock(mock_hash):
    """Test with mocked function"""
    mock_hash.return_value = "hashed_password"
    
    # Test code that uses hash_password
    result = create_user(...)
    
    mock_hash.assert_called_once()

@patch('requests.post')
def test_external_api(mock_post):
    """Test external API call"""
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"success": True}
    )
    
    result = call_external_api()
    assert result["success"] is True
```

## Running Tests

### Quick Reference

```bash
# All tests
pytest

# Specific module
pytest tests/backend/

# Specific file
pytest tests/backend/test_auth_service.py

# Specific test
pytest tests/backend/test_auth_service.py::test_create_user

# With markers
pytest -m "not slow"

# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Show print output
pytest -s

# Verbose
pytest -v

# Coverage
pytest --cov=app --cov-report=html
```

## Test Data Management

### Factories

```python
# tests/factories.py

from factory import Factory, Faker, SubFactory
from app.database.models import UserModel, TaskModel

class UserFactory(Factory):
    class Meta:
        model = UserModel
    
    username = Faker('user_name')
    password_hash = Faker('password')
    name = Faker('first_name')
    lastname = Faker('last_name')

class TaskFactory(Factory):
    class Meta:
        model = TaskModel
    
    name = Faker('sentence', nb_words=4)
    description = Faker('text')
    priority = 'medium'
    status = 'not_started'
    user = SubFactory(UserFactory)
```

## Debugging Tests

```python
# Add breakpoint in test
def test_something():
    result = function_under_test()
    import pdb; pdb.set_trace()  # Debugger stops here
    assert result == expected

# Run with debugger
pytest --pdb  # Drop into debugger on failure
pytest --trace  # Drop into debugger at start of test
```

## Performance Testing

```python
import pytest
from time import time

def test_performance():
    """Test that operation completes within time limit"""
    start = time()
    
    # Operation under test
    result = expensive_operation()
    
    elapsed = time() - start
    assert elapsed < 1.0, f"Operation took {elapsed}s, expected < 1s"
```
