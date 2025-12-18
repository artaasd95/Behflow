# Project Architecture — Behflow

## 🎯 System Goals

- **AI-Powered**: Intelligent task management using LangGraph and LLM orchestration
- **Self-Hosted**: Complete data ownership and control
- **Lightweight**: Minimal dependencies, fast startup, low resource usage
- **Scalable**: Horizontal scaling support via Docker Swarm/Kubernetes
- **Maintainable**: Clean separation of concerns, modular architecture
- **Developer-Friendly**: Comprehensive documentation, clear structure

---

## 🏗 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│         (Vanilla JS + HTML5 + CSS3 + Nginx)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Task UI    │  │   Chat UI    │  │    Auth UI   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │     REST API     │     REST API     │  REST API
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                      Backend (FastAPI)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │  Auth      │  │  Task      │  │  Automated         │    │
│  │  Router    │  │  Router    │  │  Process Scheduler │    │
│  └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘    │
│        │               │                     │               │
│  ┌─────▼───────────────▼─────────────────────▼──────────┐   │
│  │            Database Service Layer                     │   │
│  │  (Auth, Task, Chat, Process Services)                 │   │
│  └─────────────────────┬───────────────────────────────┘   │
└────────────────────────┼───────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
    ┌───────▼──────┐   ┌─▼─────────┐ │
    │  PostgreSQL  │   │   Agent   │ │
    │   Database   │   │  Service  │ │
    │              │   │(LangGraph)│ │
    └──────────────┘   └───┬───────┘ │
                           │         │
                      ┌────▼─────┐   │
                      │   LLM    │   │
                      │Providers │   │
                      └──────────┘   │
```

---

## 🧩 Component Details

### 1. Frontend Layer

**Technology**: Vanilla JavaScript, HTML5, CSS3, Nginx

**Responsibilities**:
- User interface for task management
- AI chat interface
- Authentication flows
- Theme management (dark/light)
- State management via LocalStorage

**Key Files**:
- `index.html` - Main application
- `app.js` - Task and chat logic
- `login.js` / `register.js` - Authentication
- `theme.js` - Theme switching
- `styles.css` - Atom One Dark Pro theme

**Communication**:
- REST API calls to backend
- Token-based authentication
- Real-time updates (planned: WebSocket)

---

### 2. Backend Layer (FastAPI)

**Technology**: FastAPI, Python 3.11+, Uvicorn

**Responsibilities**:
- RESTful API endpoints
- Business logic orchestration
- Authentication and authorization
- Database operations
- Background task scheduling
- Integration with AI agent

**API Routers**:
```
/register                 - User registration
/login                    - User authentication
/me                       - Current user info
/api/v1/tasks             - Task CRUD operations
/api/v1/chat              - AI chat interactions
/api/v1/processes         - Automated processes
/health                   - Health check
```

**Services**:
- `AuthService` - User management
- `TaskService` - Task operations
- `ChatService` - Chat sessions
- `AutomatedProcessService` - Process management

**Middleware**:
- CORS handling
- Error handling
- Request logging
- Rate limiting (optional)

---

### 3. Database Layer

**Technology**: PostgreSQL 15+, SQLAlchemy ORM

**Schema**:
- `users` - User accounts
- `tasks` - Task storage
- `chat_sessions` - Chat sessions
- `chat_messages` - Message history
- `automated_processes` - Process definitions
- `automated_process_executions` - Execution logs

**Features**:
- Connection pooling
- Transaction management
- Migration support (Alembic)
- Timezone-aware timestamps
- JSONB for flexible data

---

### 4. Agent Service (LangGraph)

**Technology**: LangGraph, LangChain, OpenAI/Anthropic

**Responsibilities**:
- Natural language understanding
- Intent classification
- Tool execution
- Response generation
- Context management

**Graph Nodes**:
1. **Entry Node** - Initialize conversation
2. **Intent Classification** - Understand user request
3. **Tool Execution** - Execute actions
4. **Response Generation** - Generate natural language response

**Tools**:
- `add_task` - Create new tasks
- `update_task` - Modify existing tasks
- `list_tasks` - Query tasks
- `delete_task` - Remove tasks

**State Management**:
- Conversation history
- User context
- Active tasks
- Pending actions

---

### 5. Scheduler Service

**Technology**: APScheduler

**Responsibilities**:
- Time-based process execution
- Cron-like scheduling
- Job monitoring
- Error handling and retries

**Processes**:
- Task rescheduling
- Session cleanup
- Reminder notifications
- Analytics generation

---

## 🔄 Request Flow Diagrams

### User Registration Flow

```
User → Frontend → Backend → Database
  │       │         │          │
  │       │         │  Create User
  │       │         │◄─────────┤
  │       │  Return Token       │
  │       │◄────────┤           │
  │  Display Success│           │
  │◄──────┤         │           │
```

### Task Creation via Chat

```
User → Frontend → Backend → Agent → LLM Provider
  │       │         │        │         │
  │  "Create task" │         │         │
  │──────►│         │         │         │
  │       │  POST /chat       │         │
  │       │────────►│         │         │
  │       │         │ Invoke  │         │
  │       │         │────────►│         │
  │       │         │         │  Analyze
  │       │         │         │────────►│
  │       │         │         │◄────────│
  │       │         │         │         │
  │       │         │    add_task()     │
  │       │         │◄────────│         │
  │       │         │                   │
  │       │         │  Save to DB       │
  │       │         ├──────► Database   │
  │       │  Response with task         │
  │       │◄────────┤                   │
  │  Show task card │                   │
  │◄──────┤         │                   │
```

### Automated Process Execution

```
Scheduler → AutomatedProcessService → Process Executor → Database
    │              │                        │               │
  Trigger          │                        │               │
    │──────────────►│                        │               │
    │              │  Get Process Config    │               │
    │              ├───────────────────────►│               │
    │              │                        │               │
    │              │       Execute          │               │
    │              │◄───────────────────────│               │
    │              │                        │               │
    │              │                   Update Tasks         │
    │              │                        ├──────────────►│
    │              │  Log Execution         │               │
    │              ├────────────────────────────────────────►│
```

---

## 🗂 Repository Structure (implemented)

```
/ (repo root)
├─ docs/                        # 📚 Comprehensive documentation
│  ├─ architecture.md           # System architecture (this file)
│  ├─ API.md                    # REST API documentation
│  ├─ AGENT.md                  # AI agent system guide
│  ├─ DATABASE.md               # Database schema & services
│  ├─ FRONTEND.md               # Frontend architecture
│  ├─ INTEGRATION.md            # Integration guide
│  ├─ DEPLOYMENT.md             # Deployment strategies
│  ├─ CONFIGURATION.md          # Configuration options
│  ├─ TESTING.md                # Testing guide
│  ├─ automated_processes.md    # Process automation
│  └─ README.md                 # Documentation index
├─ src/
│  ├─ frontend/                 # 🌐 Static frontend
│  │  ├─ index.html            # Main app page
│  │  ├─ login.html            # Authentication
│  │  ├─ app.js                # Task & chat logic
│  │  ├─ theme.js              # Theme management
│  │  ├─ styles.css            # Styling
│  │  ├─ nginx.conf            # Server config
│  │  └─ Dockerfile            # Container definition
│  ├─ backend/                  # 🖥 FastAPI backend
│  │  ├─ app/
│  │  │  ├─ api/
│  │  │  │  ├─ routers/        # API endpoints
│  │  │  │  │  ├─ auth.py      # Authentication routes
│  │  │  │  │  └─ chat.py      # Chat routes
│  │  │  │  └─ models/         # Request/response models
│  │  │  ├─ database/
│  │  │  │  ├─ models.py       # SQLAlchemy models
│  │  │  │  ├─ database.py     # Connection management
│  │  │  │  ├─ auth_service.py # User operations
│  │  │  │  ├─ task_service.py # Task operations
│  │  │  │  ├─ chat_service.py # Chat operations
│  │  │  │  └─ automated_process_service.py
│  │  │  ├─ main.py            # FastAPI app
│  │  │  └─ scheduler.py       # Background scheduler
│  │  ├─ requirements.txt      # Python dependencies
│  │  └─ Dockerfile
│  ├─ behflow_agent/            # 🤖 AI Agent service
│  │  ├─ nodes/
│  │  │  └─ graph_nodes.py     # LangGraph nodes
│  │  ├─ models/
│  │  │  ├─ task.py            # Task model
│  │  │  ├─ automated_process.py
│  │  │  └─ models.py          # Agent state
│  │  ├─ agent.py              # Main agent class
│  │  ├─ builder.py            # Agent factory
│  │  ├─ tools.py              # LangChain tools
│  │  ├─ llm_config.py         # LLM configuration
│  │  ├─ users.py              # User context
│  │  └─ utils.py              # Utilities
│  └─ shared/
│     └─ logger.py             # Logging utilities
├─ tests/                       # 🧪 Test suites
│  ├─ backend/                 # Backend unit tests
│  ├─ frontend/                # Frontend tests
│  └─ agent/                   # Agent tests
├─ infra/
│  ├─ docker-compose.yml       # Local development
│  └─ migrations/              # Database migrations
├─ .github/
│  └─ workflows/               # CI/CD pipelines
├─ .env.example                # Environment template
├─ README.md                   # Project overview
└─ LICENSE                     # MIT License
```

---

## � Security Architecture

### Authentication Flow

```
1. User provides credentials
2. Backend validates against database
3. Generate JWT token with expiration
4. Client stores token in LocalStorage
5. Include token in Authorization header for API requests
6. Backend validates token on each request
```

### Security Measures

- **Password Hashing**: BCrypt with salt
- **JWT Tokens**: Short expiration (24h default)
- **HTTPS Only**: TLS 1.2+ in production
- **CORS Protection**: Whitelisted origins
- **SQL Injection Prevention**: Parameterized queries
- **Rate Limiting**: Per-IP and per-user limits
- **Input Validation**: Pydantic models
- **Secret Management**: Environment variables, never hardcoded

---

## 📊 Data Flow Patterns

### Task Lifecycle

```
1. CREATE: User creates task via chat or form
   ↓
2. STORE: Save to database with NOT_STARTED status
   ↓
3. UPDATE: Status changes (IN_PROGRESS, COMPLETED, BLOCKED)
   ↓
4. NOTIFY: Trigger webhooks/notifications
   ↓
5. ARCHIVE/DELETE: Cleanup or permanent removal
```

### Chat Session Lifecycle

```
1. INITIATE: User sends first message
   ↓
2. CREATE SESSION: Generate session_id
   ↓
3. PROCESS: Agent analyzes and responds
   ↓
4. STORE: Save messages to database
   ↓
5. CONTINUE: Maintain context across messages
   ↓
6. EXPIRE: Auto-cleanup after inactivity
```

---

## 🚀 Scalability Strategy

### Horizontal Scaling

**Backend**:
- Stateless design
- Load balancing with Nginx/Traefik
- Auto-scaling based on CPU/memory

**Database**:
- Read replicas for queries
- Connection pooling
- Query optimization

**Agent Service**:
- Async/await for concurrency
- LLM request batching
- Response caching

### Vertical Scaling

- Increase container resources
- Optimize database indices
- Cache frequently accessed data

---

## 🔧 Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Vanilla JS + HTML5 + CSS3 | Lightweight UI |
| Backend | FastAPI + Python 3.11 | REST API |
| Database | PostgreSQL 15 | Data persistence |
| Agent | LangGraph + LangChain | AI orchestration |
| LLM | OpenAI/Anthropic | Natural language |
| Scheduler | APScheduler | Background jobs |
| Server | Nginx | Static files + proxy |
| Container | Docker + Docker Compose | Deployment |
| Orchestration | K8s / Docker Swarm | Scaling |

---

## 🎯 Design Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **Single Responsibility**: Each component has one job
3. **Dependency Injection**: Loose coupling via interfaces
4. **Configuration Over Code**: Environment-based settings
5. **Fail Fast**: Validate early, fail gracefully
6. **Idempotency**: Safe to retry operations
7. **Observability**: Comprehensive logging and monitoring

---

## 🔄 Development Workflow

### Local Development

```bash
# 1. Start infrastructure
docker-compose up -d db

# 2. Run backend
cd src/backend
python -m uvicorn app.main:app --reload

# 3. Serve frontend
cd src/frontend
python -m http.server 8080

# 4. Access application
open http://localhost:8080
```

### Testing Workflow

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run integration tests
pytest tests/integration/

# Run end-to-end tests
pytest tests/e2e/
```

### Deployment Workflow

```bash
# 1. Build images
docker build -t behflow/backend:latest ./src/backend
docker build -t behflow/frontend:latest ./src/frontend

# 2. Push to registry
docker push behflow/backend:latest
docker push behflow/frontend:latest

# 3. Deploy to production
kubectl apply -f k8s/
# OR
docker stack deploy -c docker-stack.yml behflow
```

---

## 📈 Future Enhancements

### Planned Features

- [ ] WebSocket support for real-time updates
- [ ] Voice interface integration
- [ ] Multi-agent collaboration
- [ ] Vector database for long-term memory
- [ ] Mobile app (React Native/Flutter)
- [ ] Browser extension
- [ ] Offline mode with sync
- [ ] Analytics dashboard
- [ ] Custom LLM integration
- [ ] Plugin system

### Technical Improvements

- [ ] GraphQL API alongside REST
- [ ] Event sourcing for audit trail
- [ ] CQRS pattern for scalability
- [ ] Redis caching layer
- [ ] Elasticsearch for full-text search
- [ ] Prometheus metrics
- [ ] Distributed tracing (Jaeger)
- [ ] API versioning
- [ ] Rate limiting per user
- [ ] Multi-tenancy support

---

## 📚 Architecture Documentation

For detailed information about each component, see:

- [API Documentation](API.md) - REST API endpoints and usage
- [Agent Documentation](AGENT.md) - AI agent system details
- [Database Documentation](DATABASE.md) - Schema and services
- [Frontend Documentation](FRONTEND.md) - UI architecture
- [Integration Guide](INTEGRATION.md) - External integrations
- [Deployment Guide](DEPLOYMENT.md) - Deployment strategies
- [Configuration Guide](CONFIGURATION.md) - Configuration options
- [Testing Guide](TESTING.md) - Testing strategies

---

*This architecture is designed to be simple, scalable, and maintainable. It prioritizes developer experience while maintaining production-readiness.*
