# Database Documentation

## Overview

Behflow uses PostgreSQL as the primary database, managed through SQLAlchemy ORM. The database stores users, tasks, chat sessions, and automated process executions.

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│      Users      │
├─────────────────┤
│ user_id (PK)    │───┐
│ username        │   │
│ password_hash   │   │
│ name            │   │
│ lastname        │   │
│ created_at      │   │
└─────────────────┘   │
                      │
                      │ 1:N
                      │
         ┌────────────┴────────────┐
         │                         │
┌────────▼────────┐    ┌──────────▼──────────────┐
│      Tasks      │    │   ChatSessions          │
├─────────────────┤    ├─────────────────────────┤
│ task_id (PK)    │    │ session_id (PK)         │
│ user_id (FK)    │    │ user_id (FK)            │
│ name            │    │ created_at              │
│ description     │    │ last_activity           │
│ status          │    └─────────────────────────┘
│ priority        │
│ due_date        │              │ 1:N
│ due_date_jalali │              │
│ tags            │    ┌─────────▼──────────────┐
│ created_at      │    │   ChatMessages         │
│ updated_at      │    ├────────────────────────┤
└─────────────────┘    │ message_id (PK)        │
                       │ session_id (FK)        │
                       │ role                   │
                       │ content                │
                       │ timestamp              │
                       └────────────────────────┘

┌─────────────────────────────┐
│    AutomatedProcesses       │
├─────────────────────────────┤
│ process_id (PK)             │
│ name                        │
│ description                 │
│ trigger_type                │
│ schedule                    │
│ is_active                   │
│ created_at                  │
└─────────────────────────────┘
         │ 1:N
         │
┌────────▼────────────────────┐
│ AutomatedProcessExecutions  │
├─────────────────────────────┤
│ execution_id (PK)           │
│ process_id (FK)             │
│ status                      │
│ started_at                  │
│ completed_at                │
│ error_message               │
│ result_data                 │
└─────────────────────────────┘
```

## Tables

### Users

**Table Name**: `users`

**Description**: Stores user account information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | PRIMARY KEY | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| name | VARCHAR(100) | NOT NULL | First name |
| lastname | VARCHAR(100) | NOT NULL | Last name |
| email | VARCHAR(255) | UNIQUE, NULL | Email address (future) |
| created_at | TIMESTAMP | NOT NULL | Account creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes**:
- `idx_users_username` on `username`
- `idx_users_email` on `email`

**SQLAlchemy Model**:
```python
class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSessionModel", back_populates="user")
```

---

### Tasks

**Table Name**: `tasks`

**Description**: Stores user tasks and to-do items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| task_id | UUID | PRIMARY KEY | Unique task identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | Owner user ID |
| name | VARCHAR(255) | NOT NULL | Task name |
| description | TEXT | NULL | Detailed description |
| status | VARCHAR(20) | NOT NULL | not_started, in_progress, completed, blocked |
| priority | VARCHAR(20) | NOT NULL | low, medium, high, urgent |
| due_date | TIMESTAMP | NULL | Due date (Gregorian) |
| due_date_jalali | VARCHAR(20) | NULL | Due date (Jalali/Persian) |
| tags | ARRAY(TEXT) | NULL | Task tags/labels |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes**:
- `idx_tasks_user_id` on `user_id`
- `idx_tasks_status` on `status`
- `idx_tasks_priority` on `priority`
- `idx_tasks_due_date` on `due_date`

**Enums**:
```python
class TaskStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
```

**SQLAlchemy Model**:
```python
class TaskModel(Base):
    __tablename__ = "tasks"
    
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.NOT_STARTED, index=True)
    priority = Column(Enum(Priority), nullable=False, default=Priority.MEDIUM, index=True)
    due_date = Column(DateTime(timezone=True), index=True)
    due_date_jalali = Column(String(20))
    tags = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="tasks")
```

---

### Chat Sessions

**Table Name**: `chat_sessions`

**Description**: Stores chat conversation sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| session_id | UUID | PRIMARY KEY | Unique session identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | Session owner |
| created_at | TIMESTAMP | NOT NULL | Session start time |
| last_activity | TIMESTAMP | NOT NULL | Last message time |

**Indexes**:
- `idx_chat_sessions_user_id` on `user_id`
- `idx_chat_sessions_last_activity` on `last_activity`

**SQLAlchemy Model**:
```python
class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="chat_sessions")
    messages = relationship("ChatMessageModel", back_populates="session", cascade="all, delete-orphan")
```

---

### Chat Messages

**Table Name**: `chat_messages`

**Description**: Stores individual chat messages

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| message_id | UUID | PRIMARY KEY | Unique message identifier |
| session_id | UUID | FOREIGN KEY, NOT NULL | Parent session |
| role | VARCHAR(20) | NOT NULL | user, assistant, system |
| content | TEXT | NOT NULL | Message content |
| timestamp | TIMESTAMP | NOT NULL | Message time |
| metadata | JSONB | NULL | Additional data |

**Indexes**:
- `idx_chat_messages_session_id` on `session_id`
- `idx_chat_messages_timestamp` on `timestamp`

**SQLAlchemy Model**:
```python
class ChatMessageModel(Base):
    __tablename__ = "chat_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSONB)
    
    # Relationships
    session = relationship("ChatSessionModel", back_populates="messages")
```

---

### Automated Processes

**Table Name**: `automated_processes`

**Description**: Stores automated process definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| process_id | UUID | PRIMARY KEY | Unique process identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Process name |
| description | TEXT | NULL | Process description |
| trigger_type | VARCHAR(20) | NOT NULL | manual, time_based, event_based |
| schedule | VARCHAR(50) | NULL | Cron expression |
| is_active | BOOLEAN | NOT NULL | Active status |
| config | JSONB | NULL | Process configuration |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes**:
- `idx_automated_processes_name` on `name`
- `idx_automated_processes_is_active` on `is_active`

**Enums**:
```python
class TriggerTypeEnum(enum.Enum):
    MANUAL = "manual"
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
```

**SQLAlchemy Model**:
```python
class AutomatedProcessModel(Base):
    __tablename__ = "automated_processes"
    
    process_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    trigger_type = Column(Enum(TriggerTypeEnum), nullable=False)
    schedule = Column(String(50))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    config = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("AutomatedProcessExecutionModel", back_populates="process")
```

---

### Automated Process Executions

**Table Name**: `automated_process_executions`

**Description**: Stores execution history of automated processes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| execution_id | UUID | PRIMARY KEY | Unique execution identifier |
| process_id | UUID | FOREIGN KEY, NOT NULL | Parent process |
| status | VARCHAR(20) | NOT NULL | success, failed, running |
| started_at | TIMESTAMP | NOT NULL | Execution start time |
| completed_at | TIMESTAMP | NULL | Execution end time |
| error_message | TEXT | NULL | Error details if failed |
| result_data | JSONB | NULL | Execution results |

**Indexes**:
- `idx_process_executions_process_id` on `process_id`
- `idx_process_executions_status` on `status`
- `idx_process_executions_started_at` on `started_at`

**SQLAlchemy Model**:
```python
class AutomatedProcessExecutionModel(Base):
    __tablename__ = "automated_process_executions"
    
    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("automated_processes.process_id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result_data = Column(JSONB)
    
    # Relationships
    process = relationship("AutomatedProcessModel", back_populates="executions")
```

## Database Services

### User Service

**File**: `backend/app/database/auth_service.py`

```python
class AuthService:
    """User authentication and management"""
    
    @staticmethod
    def create_user(db: Session, username: str, password: str, name: str, lastname: str) -> UserModel:
        """Create a new user"""
        
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[UserModel]:
        """Authenticate user credentials"""
        
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserModel]:
        """Get user by ID"""
```

### Task Service

**File**: `backend/app/database/task_service.py`

```python
class TaskService:
    """Task CRUD operations"""
    
    @staticmethod
    def create_task(db: Session, user_id: UUID, task_data: dict) -> TaskModel:
        """Create a new task"""
        
    @staticmethod
    def get_user_tasks(db: Session, user_id: UUID, filters: dict = None) -> List[TaskModel]:
        """Get all tasks for a user with optional filters"""
        
    @staticmethod
    def update_task(db: Session, task_id: UUID, user_id: UUID, updates: dict) -> TaskModel:
        """Update task fields"""
        
    @staticmethod
    def delete_task(db: Session, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task"""
```

### Chat Service

**File**: `backend/app/database/chat_service.py`

```python
class ChatService:
    """Chat session and message management"""
    
    @staticmethod
    def create_session(db: Session, user_id: UUID) -> ChatSessionModel:
        """Create a new chat session"""
        
    @staticmethod
    def add_message(db: Session, session_id: UUID, role: str, content: str) -> ChatMessageModel:
        """Add a message to a session"""
        
    @staticmethod
    def get_session_history(db: Session, session_id: UUID) -> List[ChatMessageModel]:
        """Get all messages in a session"""
```

### Automated Process Service

**File**: `backend/app/database/automated_process_service.py`

```python
class AutomatedProcessService:
    """Automated process management"""
    
    @staticmethod
    def create_process(db: Session, process_data: dict) -> AutomatedProcessModel:
        """Create a new automated process"""
        
    @staticmethod
    def get_active_processes(db: Session) -> List[AutomatedProcessModel]:
        """Get all active processes"""
        
    @staticmethod
    def record_execution(db: Session, process_id: UUID, result: dict) -> AutomatedProcessExecutionModel:
        """Record a process execution"""
```

## Database Configuration

### Connection String

```python
# Format
DATABASE_URL = "postgresql://username:password@host:port/database"

# Example (Development)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/behflow"

# Example (Production)
DATABASE_URL = "postgresql://behflow_user:secure_password@db.example.com:5432/behflow_prod"
```

### Connection Pool

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before use
    pool_size=10,            # Connection pool size
    max_overflow=20,         # Additional connections when pool full
    echo=False               # Log SQL queries (set True for debugging)
)
```

## Migrations

### Alembic Setup

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Migration Example

```python
"""Add tasks table

Revision ID: 001
Create Date: 2025-12-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])

def downgrade():
    op.drop_table('tasks')
```

## Database Initialization

### Seed Data

**File**: `backend/app/database/init_db.py`

```python
def seed_database(db: Session):
    """Seed database with initial data"""
    
    # Create default automated processes
    processes = [
        {
            "name": "reschedule_tasks",
            "description": "Reschedule overdue tasks",
            "trigger_type": "time_based",
            "schedule": "0 0 * * *"  # Daily at midnight
        }
    ]
    
    for process_data in processes:
        process = AutomatedProcessModel(**process_data)
        db.add(process)
    
    db.commit()
```

## Performance Optimization

### Indexes

```sql
-- User lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Task queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Chat queries
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

-- Process queries
CREATE INDEX idx_process_executions_process_id ON automated_process_executions(process_id);
```

### Query Optimization

```python
# Use eager loading to prevent N+1 queries
tasks = db.query(TaskModel).options(
    joinedload(TaskModel.user)
).filter(TaskModel.user_id == user_id).all()

# Use pagination for large result sets
def get_tasks_paginated(db: Session, user_id: UUID, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    return db.query(TaskModel)\
        .filter(TaskModel.user_id == user_id)\
        .offset(offset)\
        .limit(size)\
        .all()
```

## Backup and Recovery

### Backup Script

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="behflow"

pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/behflow_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "behflow_*.sql.gz" -mtime +7 -delete
```

### Restore

```bash
# Restore from backup
gunzip < behflow_20251218_120000.sql.gz | psql -U postgres behflow
```

## Security

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### SQL Injection Prevention

SQLAlchemy ORM automatically prevents SQL injection through parameterized queries:

```python
# Safe - parameterized
user = db.query(UserModel).filter(UserModel.username == username).first()

# Unsafe - avoid raw SQL with string formatting
# db.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

## Monitoring

### Query Logging

```python
# Enable SQL logging
engine = create_engine(DATABASE_URL, echo=True)
```

### Connection Pool Monitoring

```python
def get_pool_stats(engine):
    """Get connection pool statistics"""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow()
    }
```

## Timezone Handling

All timestamps are stored in UTC and converted to user timezone on retrieval:

```python
from datetime import timezone

# Store in UTC
task.created_at = datetime.now(timezone.utc)

# Convert to user timezone
user_tz = pytz.timezone('Asia/Tehran')
local_time = task.created_at.astimezone(user_tz)
```

## Future Enhancements

- [ ] Full-text search with PostgreSQL tsvector
- [ ] Partitioning for large tables
- [ ] Read replicas for scaling
- [ ] Redis caching layer
- [ ] GraphQL API support
- [ ] Audit logging for compliance
