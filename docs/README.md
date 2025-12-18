# Behflow Documentation

Welcome to the comprehensive documentation for Behflow - an AI-powered, self-hosted task management system.

**Repository:** https://github.com/artaasd95/Behflow

## 📑 Documentation Index

### Core Documentation

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | Complete system architecture, components, and design principles |
| [API Documentation](API.md) | REST API endpoints with examples and response formats |
| [Agent System](AGENT.md) | AI agent internals, tools, and LangGraph implementation |
| [Database Schema](DATABASE.md) | Database models, relationships, and services |
| [Frontend Guide](FRONTEND.md) | UI architecture, state management, and components |

### Integration & Deployment

| Document | Description |
|----------|-------------|
| [Integration Guide](INTEGRATION.md) | External service integrations (Slack, Calendar, Jira, etc.) |
| [Deployment Guide](DEPLOYMENT.md) | Docker, Kubernetes, cloud platform deployment strategies |
| [Configuration](CONFIGURATION.md) | Environment variables, feature flags, and settings |

### Development

| Document | Description |
|----------|-------------|
| [Testing Guide](TESTING.md) | Unit tests, integration tests, coverage requirements |
| [Automated Processes](automated_processes.md) | Background task scheduling and automation |
| [Changes & Tasks](CHANGES.md) | Version history and development roadmap |

## 🚀 Quick Links

- **Getting Started**: See main [README.md](../README.md)
- **API Reference**: [API.md](API.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Testing**: [TESTING.md](TESTING.md)

## 📖 Reading Guide

### For New Users
1. Start with [Architecture](architecture.md) for system overview
2. Read [API Documentation](API.md) for API usage
3. Check [Frontend Guide](FRONTEND.md) for UI details

### For Developers
1. Review [Architecture](architecture.md) for design principles
2. Study [Agent System](AGENT.md) for AI implementation
3. Read [Database Schema](DATABASE.md) for data models
4. Follow [Testing Guide](TESTING.md) for test practices
5. See [Configuration](CONFIGURATION.md) for setup options

### For DevOps
1. Check [Deployment Guide](DEPLOYMENT.md) for infrastructure
2. Review [Configuration](CONFIGURATION.md) for environment setup
3. See [Automated Processes](automated_processes.md) for background jobs

### For Integration
1. Read [Integration Guide](INTEGRATION.md) for external services
2. Check [API Documentation](API.md) for API endpoints
3. Review [Configuration](CONFIGURATION.md) for webhook setup

## 🏗 System Overview

```
Behflow = Frontend (UI) + Backend (API) + Agent (AI) + Database (PostgreSQL)
```

- **Frontend**: Vanilla JS single-page application
- **Backend**: FastAPI REST API with business logic
- **Agent**: LangGraph-powered AI task orchestration
- **Database**: PostgreSQL with SQLAlchemy ORM

## 🔧 Tech Stack

- **Languages**: Python 3.11+, JavaScript (ES6+)
- **Frameworks**: FastAPI, LangGraph, LangChain
- **Database**: PostgreSQL 15+
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Infrastructure**: Docker, Kubernetes
- **Testing**: pytest, Jest

## 📝 Documentation Standards

All documentation follows these principles:

1. **Clear Structure**: Hierarchical organization with headings
2. **Code Examples**: Real, runnable code snippets
3. **Diagrams**: Visual representations where helpful
4. **Up-to-Date**: Synchronized with codebase changes
5. **Searchable**: Descriptive titles and comprehensive content

## 🤝 Contributing to Docs

When adding new features:

1. Update relevant documentation files
2. Add code examples and usage patterns
3. Update architecture diagrams if needed
4. Add entries to this README index
5. Keep documentation synchronized with code

## 📚 Additional Resources

- **Main README**: [../README.md](../README.md)
- **GitHub Repository**: https://github.com/artaasd95/Behflow
- **Issue Tracker**: https://github.com/artaasd95/Behflow/issues

## Recent Changes

- **2025-12-18**: Completed comprehensive documentation suite
- **2025-12-18**: Added testing guide and unit tests
- **2025-12-18**: Created integration and deployment guides
- **2025-12-18**: Documented agent system and database schema
- **2025-12-18**: Expanded architecture with diagrams and patterns

---

*For questions or clarifications, please open an issue on GitHub.*
