# Project Architecture — Behflow

## 🎯 Goals
- Minimal, **lightweight** backend using **FastAPI** + **LangGraph** for orchestration.
- Simple frontend (static single-page app) with minimal build tooling.
- Database provided via **Docker Compose** (Postgres) so local/dev setup is easy.
- Clean GitHub repo structure with docs, CI-ready placeholders, and modular src layout.

---

## 🔧 Components Overview

### Request Flow
**Frontend → Backend (FastAPI) → Behflow Agent (LangGraph Service)**

1. **Frontend**
   - Simple SPA (e.g., vanilla JS/TS, Vite, or small React app)
   - Responsible for user interactions and lightweight UI
   - Communicates with backend via REST API

2. **Backend (FastAPI)**
   - Lightweight HTTP API layer with FastAPI
   - **Endpoints:**
     - `GET /health` - Health check
     - `POST /api/v1/chat` - Main chat endpoint (router-based)
   - Router calls the behflow-agent service via factory pattern
   - Minimal dependencies, clean separation of concerns

3. **Behflow Agent Service (LangGraph)**
   - Separate service package: `behflow_agent`
   - **Components:**
     - `nodes/` - Graph node definitions (BaseNode, ProcessingNode, ResponseNode)
     - `agent.py` - Main LangGraph agent class with graph construction
     - `builder.py` - Factory pattern for creating agent instances
   - All logic is blank/placeholder for now (base classes only)
   - Uses LangGraph for orchestrating LLM workflows

4. **Database**
   - Postgres run via Docker Compose for local development
   - No persistence strategy enforced here — keep models simple and migratable (Alembic later if needed)

5. **Infra / DevOps**
   - `docker-compose.yml` to run DB and optionally other lightweight infra
   - `.github` templates and workflow placeholders for CI

---

## 🗂 Repository Structure (implemented)

```
/ (repo root)
├─ docs/
│  ├─ architecture.md           # <-- this file
│  └─ README.md                # project docs index
├─ src/
│  ├─ frontend/                # static frontend skeleton (TBD)
│  ├─ backend/                 # FastAPI backend
│  │  ├─ app/
│  │  │  ├─ api/
│  │  │  │  └─ routers/
│  │  │  │     └─ chat.py      # Chat router with POST /chat endpoint
│  │  │  ├─ main.py           # FastAPI app entry + health endpoint
│  │  │  └─ __init__.py
│  │  ├─ requirements.txt     # FastAPI + LangGraph minimal deps
│  │  └─ README.md
│  └─ behflow_agent/          # LangGraph agent service
│     ├─ nodes/
│     │  └─ __init__.py       # BaseNode, ProcessingNode, ResponseNode
│     ├─ agent.py             # BehflowAgent (main graph class)
│     ├─ builder.py           # AgentBuilder (factory pattern)
│     ├─ __init__.py
│     └─ README.md
├─ infra/
│  └─ docker-compose.yml       # Postgres DB (minimal)
├─ .github/
│  ├─ ISSUE_TEMPLATE.md
│  └─ PULL_REQUEST_TEMPLATE.md
└─ README.md
```

> **Note:** For now the repo contains only structure and documentation. No application code is included at this stage.

---

## 📌 Lightweight dependency guidance
- Use a minimal Python environment (venv or Poetry). Avoid heavy ML model downloads in repo.
- Keep LangGraph integration as a small client or remote connector (run models externally) to avoid bundling large model weights.
- Pin only what you need for development: FastAPI, Uvicorn (ASGI server), LangGraph client package.

---

## 🧭 Development workflow (high level)
1. Developer starts DB with `docker compose up -d` (infra/docker-compose.yml)
2. Backend runs locally (Uvicorn) and connects to DB
3. Frontend served locally (Vite or static server)
4. LangGraph tasks call external LLM provider or lightweight local runner

---

## Next steps
- Review this architecture and confirm the stack choices (FastAPI + LangGraph + Postgres).
- After approval: scaffold minimal app code, add a minimal docker-compose file for Postgres, and create CI workflow skeleton.

---

*Document created to guide scaffolding and early implementation.*
