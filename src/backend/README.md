# Behflow Backend

Lightweight FastAPI backend that orchestrates requests to the behflow-agent service.

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
- `POST /api/v1/chat` - Chat with the agent

## Environment

Make sure Python 3.11+ is installed. The backend connects to the behflow-agent service.
