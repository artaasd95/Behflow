# Behflow Database Configuration

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/behflow
# For SQLite: DATABASE_URL=sqlite:///./behflow.db

# SQL Echo (for debugging)
SQL_ECHO=false

# Timezone (for task dates)
BEHFLOW_TIMEZONE=Asia/Tehran
```

## Database Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-db.txt
```

### 2. PostgreSQL Setup

If using PostgreSQL, create the database:

```sql
CREATE DATABASE behflow;
CREATE USER behflow_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE behflow TO behflow_user;
```

### 3. Initialize Database

```bash
# Initialize database (create tables)
python -m app.database.init_db

# Reset database (drop and recreate all tables)
python -m app.database.init_db --reset

# Initialize without test data
python -m app.database.init_db --no-test-data
```

## Database Schema

### Users Table
- `user_id` (UUID, Primary Key)
- `username` (String, Unique, Indexed)
- `password_hash` (String)
- `name` (String)
- `lastname` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `is_active` (Boolean)

### Tasks Table
- `task_id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key → users)
- `name` (String)
- `description` (Text)
- `due_date_gregorian` (DateTime with timezone)
- `due_date_jalali` (String)
- `date_added_gregorian` (DateTime with timezone)
- `date_added_jalali` (String)
- `priority` (Enum: low, medium, high)
- `status` (Enum: pending, in_progress, completed, cancelled)
- `tags` (Array of Strings)
- `completed_at` (DateTime)
- `updated_at` (DateTime)

### Chat Sessions Table
- `session_id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key → users)
- `title` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `is_active` (Boolean)

### Chat Messages Table
- `message_id` (UUID, Primary Key)
- `session_id` (UUID, Foreign Key → chat_sessions)
- `role` (String: 'user' or 'assistant')
- `content` (Text)
- `created_at` (DateTime)
- `tokens_used` (Integer)

## Services

### AuthService
- `create_user(db, user_data)` - Create new user
- `authenticate_user(db, username, password)` - Authenticate user
- `get_user_by_id(db, user_id)` - Get user by ID
- `get_user_by_username(db, username)` - Get user by username
- `update_user(db, user_id, ...)` - Update user information
- `deactivate_user(db, user_id)` - Deactivate user (soft delete)
- `hash_password(password)` - Hash password with bcrypt
- `verify_password(plain, hashed)` - Verify password

### TaskService
- `create_task(db, task)` - Create new task
- `get_task_by_id(db, task_id)` - Get task by ID
- `get_user_tasks(db, user_id, ...)` - Get user's tasks with filters
- `update_task(db, task_id, ...)` - Update task
- `delete_task(db, task_id)` - Delete task
- `search_tasks(db, user_id, search_term)` - Search tasks
- `get_tasks_by_tag(db, user_id, tag)` - Get tasks by tag
- `get_overdue_tasks(db, user_id)` - Get overdue tasks
- `get_task_statistics(db, user_id)` - Get task statistics

### ChatService
- `create_session(db, user_id, title)` - Create chat session
- `get_session_by_id(db, session_id)` - Get session by ID
- `get_user_sessions(db, user_id, ...)` - Get user's sessions
- `update_session_title(db, session_id, title)` - Update session title
- `deactivate_session(db, session_id)` - Deactivate session
- `delete_session(db, session_id)` - Delete session
- `add_message(db, session_id, role, content, ...)` - Add message
- `get_session_messages(db, session_id, ...)` - Get session messages
- `get_message_by_id(db, message_id)` - Get message by ID
- `delete_message(db, message_id)` - Delete message
- `get_session_token_usage(db, session_id)` - Get token usage stats

## Usage Examples

### Using Database Session

```python
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/endpoint")
async def endpoint(db: Session = Depends(get_db)):
    # Use db session here
    pass
```

### Authentication Example

```python
from app.database import AuthService
from sqlalchemy.orm import Session

# Create user
user = AuthService.create_user(db, user_data)

# Authenticate
user = AuthService.authenticate_user(db, "username", "password")
if user:
    print(f"Authenticated: {user.username}")
```

### Task Management Example

```python
from app.database import TaskService
from behflow_agent.models.task import Task

# Create task
task = Task(user_id=user_id, name="My Task", ...)
db_task = TaskService.create_task(db, task)

# Get user tasks
tasks = TaskService.get_user_tasks(db, user_id, status="pending")

# Update task
TaskService.update_task(db, task_id, status="completed")
```

### Chat Management Example

```python
from app.database import ChatService

# Create session
session = ChatService.create_session(db, user_id, "My Chat")

# Add messages
ChatService.add_message(db, session.session_id, "user", "Hello!")
ChatService.add_message(db, session.session_id, "assistant", "Hi there!")

# Get messages
messages = ChatService.get_session_messages(db, session.session_id)
```

## Migrations (Optional)

For production, use Alembic for database migrations:

```bash
# Initialize alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Docker Setup

The `docker-compose.yml` should include PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: behflow
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```
