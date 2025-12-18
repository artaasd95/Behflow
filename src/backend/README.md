# Behflow Backend

Lightweight FastAPI backend that orchestrates requests to the behflow-agent service.

**Repository:** https://github.com/artaasd95/Behflow

## Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routers/
│   │       └── chat.py        # Chat endpoint router
│   └── main.py                # FastAPI app entry point
└── requirements.txt           # Python dependencies
```

## Running locally

```bash
cd src/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

- `GET /health` - Health check
- `POST /api/v1/chat` - Chat with the agent (note: current implementation returns a placeholder response; see `docs/TASKS.md` for TODOs to implement real agent invocation)

## Notes

- The backend Dockerfile previously used `--no-cache-dir` with pip; this was removed on 2025-12-18 per maintainer request.

## Environment

Make sure Python 3.11+ is installed. The backend connects to the behflow-agent service.
