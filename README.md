# 🌟 Behflow

> *An AI-powered, self-hosted task management system that brings intelligence to your workflow*

Behflow is a modern, AI-driven to-do manager designed for simplicity, efficiency, and seamless integration. Named after "Behnaz" (My partner), this project is a heartfelt tribute to the inspiration behind its creation. Behflow empowers users to manage their tasks intelligently while leveraging cutting-edge AI technology to automate processes and enhance productivity.

## ✨ Features

### 🤖 **AI-Powered Intelligence**
- **LangGraph-based Agent System**: Conversational AI agent for intelligent task orchestration
- **Automated Process Scheduling**: Time-based triggers with cron-like scheduling
- **Smart Task Rescheduling**: Automatically reschedule tasks based on context and priorities
- **Interactive Chat Assistant**: Markdown-supported chat interface for natural task interaction

### 📋 **Task Management**
- **Multi-Status Tracking**: Organize tasks by status (Not Started, In Progress, Completed, Blocked)
- **Priority Management**: Set and manage task priorities with intelligent suggestions
- **Timezone-Aware Scheduling**: Support for both Gregorian and Jalali date systems
- **Manual & Automatic Triggers**: Execute processes on demand or via scheduled automation

### 🔐 **Authentication & Security**
- **User Authentication**: Secure login and registration system
- **Session Management**: Robust session handling and user state management
- **Self-Hosted Privacy**: Complete control over your data and deployment

### 🎨 **Modern Interface**
- **Responsive Design**: Optimized for desktop and mobile devices
- **Theme Switching**: Toggle between Atom One Dark Pro and light themes
- **Real-time Updates**: Live task status updates and notifications
- **Intuitive Navigation**: Clean, user-friendly interface design

### 🛠 **Developer-Friendly**
- **Docker-Ready**: Full containerization with Docker Compose
- **API-First Architecture**: RESTful APIs built with FastAPI
- **Modular Structure**: Clean separation of concerns and maintainable codebase
- **Extensive Documentation**: Comprehensive guides and architecture documentation

## 🏗 Project Architecture

```
Behflow/
├── 📚 docs/                    # Comprehensive documentation
│   ├── architecture.md         # System architecture overview
│   ├── automated_processes.md  # Automation system guide
│   └── TASKS.md                # Development tasks & roadmap
├── 🔧 infra/                   # Infrastructure & deployment
│   ├── docker-compose.yml      # Multi-container orchestration
│   └── migrations/             # Database schema migrations
├── 💻 src/
│   ├── 🖥 backend/             # FastAPI REST API server
│   │   ├── app/
│   │   │   ├── api/            # API routes (auth, chat, tasks)
│   │   │   ├── database/       # Database models & services
│   │   │   ├── main.py         # FastAPI application entry point
│   │   │   └── scheduler.py    # Background task scheduler
│   │   └── requirements.txt    # Python dependencies
│   ├── 🌐 frontend/            # Modern web interface
│   │   ├── index.html          # Main application page
│   │   ├── login.html          # Authentication pages
│   │   ├── app.js              # Task management & chat logic
│   │   └── styles.css          # Atom One Dark Pro theme
│   ├── 🤖 behflow_agent/       # AI Agent system (LangGraph)
│   │   ├── agent.py            # Main agent orchestrator
│   │   ├── nodes/              # Processing nodes
│   │   ├── models/             # Data models (Task, Process)
│   │   └── tools.py            # Agent tools & utilities
│   └── 🔄 shared/              # Shared utilities
└── 📜 LICENSE                  # MIT License
```

## 🚀 Quick Start

### 📋 Prerequisites

- 🐳 **Docker** & Docker Compose
- 🐍 **Python 3.9+** (for local development)
- 📦 **Node.js** (for frontend development)

### ⚡ Installation

#### 🐳 **Docker Setup (Recommended)**

```bash
# Clone the repository
git clone https://github.com/your-username/behflow.git
cd behflow

# Launch all services with Docker Compose
docker-compose up -d

# Access the application
# 🌐 Frontend: http://localhost:8080
# 🔌 API: http://localhost:8000
```

#### 🛠 **Local Development Setup**

```bash
# Backend setup
cd src/backend
pip install -r requirements.txt
python -m app.main

# Frontend setup (in new terminal)
cd src/frontend
# Serve with your preferred static server
python -m http.server 8080

# Agent service (in new terminal)
cd src/behflow_agent
pip install -r requirements.txt
```

### 🎯 **First Steps**

1. **Register** your account at `http://localhost:8080/register.html`
2. **Login** and start creating your first tasks
3. **Chat** with the AI assistant to manage tasks naturally
4. **Explore** automated processes in the documentation

## 📚 Documentation

Explore comprehensive documentation in the [docs folder](docs/):

| Document | Description |
|----------|-------------|
| 🏗 [Architecture](docs/architecture.md) | System design, components, and request flow |
| ⚙️ [Automated Processes](docs/automated_processes.md) | Scheduling, triggers, and automation system |
| 📋 [Tasks & Changes](docs/TASKS.md) | Development roadmap and change log |

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- 🐛 **Report bugs** by opening an issue
- 💡 **Suggest features** through discussions
- 🔧 **Submit pull requests** for improvements
- 📝 **Improve documentation** and examples

Please read our contribution guidelines and follow the existing code style.

## 🛠 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **AI Engine**: LangGraph, OpenAI/Anthropic integration
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Database**: PostgreSQL with timezone awareness

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 💖 Acknowledgments

*Named with love after "Behnaz" - the inspiration behind this project.*

---

<div align="center">

**🌟 Behflow: Where AI meets productivity** 

*Simplifying task management with intelligent automation*

</div>