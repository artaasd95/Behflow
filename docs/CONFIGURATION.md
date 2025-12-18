# Configuration Guide

## Overview

Behflow uses environment variables and configuration files for customization. This guide covers all configuration options across the system.

## Environment Variables

### Backend Configuration

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/behflow
SQL_ECHO=false  # Set to true to log SQL queries
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
PASSWORD_MIN_LENGTH=8

# CORS
CORS_ORIGINS=http://localhost:8080,https://behflow.example.com
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json or text
LOG_FILE=/var/log/behflow/backend.log
```

### LLM Configuration

```env
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_TEMPERATURE=0.7

# Default Provider
DEFAULT_LLM_PROVIDER=openai  # openai or anthropic

# Rate Limiting
LLM_MAX_REQUESTS_PER_MINUTE=60
LLM_MAX_TOKENS_PER_MINUTE=90000
```

### Scheduler Configuration

```env
# Automated Process Schedules (Cron format)
RESCHEDULE_TASKS_SCHEDULE=0 0 * * *  # Daily at midnight
CLEANUP_SESSIONS_SCHEDULE=0 2 * * *  # Daily at 2 AM
SEND_REMINDERS_SCHEDULE=0 9 * * *     # Daily at 9 AM

# Scheduler Settings
SCHEDULER_TIMEZONE=UTC
SCHEDULER_MAX_INSTANCES=3
SCHEDULER_COALESCE=true
SCHEDULER_MISFIRE_GRACE_TIME=300  # seconds
```

### Frontend Configuration

```env
# API Endpoint
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# Features
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_SENTRY=false

# Theme
VITE_DEFAULT_THEME=dark  # dark or light
```

### Email Configuration

```env
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@behflow.example.com
SMTP_USE_TLS=true

# Email Features
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_WELCOME_EMAIL=true
```

### Webhook Configuration

```env
# Outgoing Webhooks
WEBHOOK_URLS=https://webhook1.example.com,https://webhook2.example.com
WEBHOOK_TIMEOUT=5  # seconds
WEBHOOK_RETRY_COUNT=3

# Incoming Webhooks
GITHUB_WEBHOOK_SECRET=your-github-secret
SLACK_WEBHOOK_SECRET=your-slack-secret
```

## Configuration Files

### Backend Config (`backend/config.py`)

```python
"""
Application configuration
"""
import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = False
    
    # Database
    database_url: str
    sql_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    
    # CORS
    cors_origins: List[str] = ["http://localhost:8080"]
    cors_allow_credentials: bool = True
    
    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    anthropic_api_key: str = ""
    default_llm_provider: str = "openai"
    
    # Scheduler
    reschedule_tasks_schedule: str = "0 0 * * *"
    scheduler_timezone: str = "UTC"
    
    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    enable_email_notifications: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

### LLM Config (`behflow_agent/llm_config.py`)

```python
"""
LLM provider configuration
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMConfig:
    """LLM configuration and factory"""
    
    @staticmethod
    def get_llm(provider: Optional[str] = None):
        """
        Get configured LLM instance
        
        Args:
            provider: "openai" or "anthropic" (default from env)
        
        Returns:
            Configured LLM instance
        """
        provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        
        if provider == "openai":
            return ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    def get_embedding_model():
        """Get embedding model for vector operations"""
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-behflow}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/migrations:/docker-entrypoint-initdb.d
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./src/backend
      dockerfile: Dockerfile
      args:
        - PYTHON_VERSION=${PYTHON_VERSION:-3.11}
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-postgres}@db:5432/${DB_NAME:-behflow}
    volumes:
      - ./src/backend:/app
      - backend_logs:/var/log/behflow
    ports:
      - "${API_PORT:-8000}:8000"
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./src/frontend
      dockerfile: Dockerfile
    ports:
      - "${FRONTEND_PORT:-8080}:80"
    depends_on:
      - backend
    environment:
      - API_URL=http://backend:8000

volumes:
  postgres_data:
  backend_logs:
```

## Feature Flags

### Backend Feature Flags

```python
# backend/app/feature_flags.py

class FeatureFlags:
    """Feature flags for gradual rollout"""
    
    ENABLE_AI_AGENT = os.getenv("FEATURE_AI_AGENT", "true").lower() == "true"
    ENABLE_AUTOMATED_PROCESSES = os.getenv("FEATURE_AUTOMATED_PROCESSES", "true").lower() == "true"
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv("FEATURE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
    ENABLE_WEBHOOKS = os.getenv("FEATURE_WEBHOOKS", "false").lower() == "true"
    ENABLE_ANALYTICS = os.getenv("FEATURE_ANALYTICS", "false").lower() == "true"
    ENABLE_RATE_LIMITING = os.getenv("FEATURE_RATE_LIMITING", "true").lower() == "true"
    
    # Experimental features
    ENABLE_VOICE_INTERFACE = os.getenv("FEATURE_VOICE_INTERFACE", "false").lower() == "true"
    ENABLE_MULTI_AGENT = os.getenv("FEATURE_MULTI_AGENT", "false").lower() == "true"
```

## User Preferences

### User Settings Schema

```python
# models/user_preferences.py

class UserPreferences(BaseModel):
    """User-specific preferences"""
    
    # Display
    theme: str = "dark"  # dark, light
    language: str = "en"  # en, fa (Persian)
    
    # Date & Time
    timezone: str = "UTC"
    date_format: str = "gregorian"  # gregorian, jalali
    time_format: str = "24h"  # 12h, 24h
    
    # Notifications
    email_notifications: bool = True
    push_notifications: bool = True
    notification_frequency: str = "realtime"  # realtime, daily, weekly
    
    # AI Behavior
    ai_verbosity: str = "balanced"  # concise, balanced, detailed
    ai_provider: str = "openai"  # openai, anthropic
    
    # Task Defaults
    default_priority: str = "medium"
    default_status: str = "not_started"
    auto_reschedule: bool = True
    
    # Privacy
    analytics_enabled: bool = False
    share_usage_data: bool = False
```

## Database Configuration

### Connection Pooling

```python
# backend/app/database/database.py

from sqlalchemy.pool import QueuePool, NullPool

# Production: Use connection pool
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # Number of connections to keep open
    max_overflow=20,           # Maximum overflow connections
    pool_pre_ping=True,        # Test connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False                 # Set True for SQL logging
)

# Testing: No pool (create new connections)
test_engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=True
)
```

### Migration Configuration

```ini
# alembic.ini

[alembic]
script_location = alembic
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/behflow

# Logging
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic
```

## Logging Configuration

### Python Logging

```python
# shared/logger.py

import logging
import sys
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_format: str = "json"):
    """Configure application logging"""
    
    level = getattr(logging, log_level.upper())
    
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        '/var/log/behflow/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

class JsonFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)
```

## Security Configuration

### Password Policy

```python
# backend/app/security.py

class PasswordPolicy:
    """Password validation rules"""
    
    MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    REQUIRE_LOWERCASE = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    REQUIRE_DIGIT = os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
    REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "false").lower() == "true"
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        """Validate password against policy"""
        
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if cls.REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
```

### Rate Limiting

```python
# backend/app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        os.getenv("RATE_LIMIT_DEFAULT", "100/minute"),
        os.getenv("RATE_LIMIT_HOURLY", "1000/hour")
    ]
)

# Apply to specific endpoints
@app.post("/api/v1/chat")
@limiter.limit("10/minute")
async def chat_endpoint():
    ...
```

## Performance Configuration

### Caching

```python
# backend/app/cache.py

import redis
from functools import wraps

# Redis configuration
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

def cache(ttl: int = 300):
    """Cache decorator with TTL"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

## Monitoring Configuration

### Health Check Endpoint

```python
# backend/app/main.py

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    
    # Check database
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check LLM API
    llm_status = "healthy"  # Implement actual check
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": db_status,
            "llm": llm_status
        }
    }
```

## Configuration Best Practices

1. **Never commit secrets**: Use environment variables or secret management
2. **Use different configs per environment**: Development, staging, production
3. **Validate configuration on startup**: Fail fast if misconfigured
4. **Document all options**: Keep this guide updated
5. **Use sensible defaults**: Make it work out of the box
6. **Enable debug logging in development**: Disable in production
7. **Rotate secrets regularly**: Especially API keys and passwords

## Configuration Templates

### Development `.env`

```env
# Development configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/behflow
SECRET_KEY=dev-secret-key-not-for-production
API_PORT=8000
LOG_LEVEL=DEBUG
SQL_ECHO=true
OPENAI_API_KEY=your-dev-key
DEFAULT_LLM_PROVIDER=openai
```

### Production `.env`

```env
# Production configuration
DATABASE_URL=postgresql://user:password@db-prod.example.com:5432/behflow
SECRET_KEY=use-strong-random-key-here
API_PORT=8000
LOG_LEVEL=INFO
SQL_ECHO=false
OPENAI_API_KEY=your-prod-key
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.sendgrid.net
```

### Testing `.env`

```env
# Testing configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/behflow_test
SECRET_KEY=test-secret-key
API_PORT=8001
LOG_LEVEL=DEBUG
SQL_ECHO=true
OPENAI_API_KEY=test-key
DEFAULT_LLM_PROVIDER=mock
```
