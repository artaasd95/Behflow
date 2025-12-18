# API Documentation

## Overview

Behflow provides a RESTful API built with FastAPI. The API handles authentication, task management, chat interactions, and automated process execution.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`

## Authentication

### Register User

Create a new user account.

**Endpoint**: `POST /register`

**Request Body**:
```json
{
  "username": "string",
  "password": "string",
  "name": "string",
  "lastname": "string"
}
```

**Response** (200 OK):
```json
{
  "user_id": "uuid",
  "username": "string",
  "name": "string",
  "lastname": "string"
}
```

**Error Responses**:
- `400 Bad Request`: Username already exists

**Example**:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123",
    "name": "John",
    "lastname": "Doe"
  }'
```

---

### Login

Authenticate and get a session token.

**Endpoint**: `POST /login`

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200 OK):
```json
{
  "token": "uuid",
  "user": {
    "user_id": "uuid",
    "username": "string",
    "name": "string",
    "lastname": "string"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials

**Example**:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

---

### Get Current User

Retrieve information about the authenticated user.

**Endpoint**: `GET /me`

**Headers**:
- `Authorization`: Bearer token from login

**Response** (200 OK):
```json
{
  "user_id": "uuid",
  "username": "string",
  "name": "string",
  "lastname": "string"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token

**Example**:
```bash
curl -X GET http://localhost:8000/me \
  -H "Authorization: <token>"
```

---

## Chat

### Send Chat Message

Send a message to the AI agent and receive a response.

**Endpoint**: `POST /api/v1/chat`

**Headers**:
- `Authorization`: Bearer token from login

**Request Body**:
```json
{
  "message": "string",
  "session_id": "string" (optional)
}
```

**Response** (200 OK):
```json
{
  "response": "string",
  "session_id": "string",
  "tasks": [
    {
      "task_id": "uuid",
      "name": "string",
      "description": "string",
      "status": "not_started|in_progress|completed|blocked",
      "priority": "low|medium|high|urgent"
    }
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: <token>" \
  -d '{
    "message": "Create a task to review project documentation",
    "session_id": "abc-123"
  }'
```

---

## Tasks

### List Tasks

Get all tasks for the authenticated user.

**Endpoint**: `GET /api/v1/tasks`

**Headers**:
- `Authorization`: Bearer token from login

**Query Parameters**:
- `status` (optional): Filter by status (not_started, in_progress, completed, blocked)
- `priority` (optional): Filter by priority (low, medium, high, urgent)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "name": "string",
      "description": "string",
      "status": "not_started",
      "priority": "medium",
      "due_date": "2025-12-31T23:59:59Z",
      "created_at": "2025-12-18T10:00:00Z",
      "updated_at": "2025-12-18T10:00:00Z",
      "tags": ["project", "urgent"]
    }
  ]
}
```

---

### Create Task

Create a new task.

**Endpoint**: `POST /api/v1/tasks`

**Headers**:
- `Authorization`: Bearer token from login

**Request Body**:
```json
{
  "name": "string",
  "description": "string",
  "priority": "low|medium|high|urgent",
  "due_date": "2025-12-31T23:59:59Z" (optional),
  "tags": ["string"] (optional)
}
```

**Response** (201 Created):
```json
{
  "task_id": "uuid",
  "name": "string",
  "description": "string",
  "status": "not_started",
  "priority": "medium",
  "due_date": "2025-12-31T23:59:59Z",
  "created_at": "2025-12-18T10:00:00Z",
  "updated_at": "2025-12-18T10:00:00Z"
}
```

---

### Update Task

Update an existing task.

**Endpoint**: `PUT /api/v1/tasks/{task_id}`

**Headers**:
- `Authorization`: Bearer token from login

**Request Body** (all fields optional):
```json
{
  "name": "string",
  "description": "string",
  "status": "not_started|in_progress|completed|blocked",
  "priority": "low|medium|high|urgent",
  "due_date": "2025-12-31T23:59:59Z",
  "tags": ["string"]
}
```

**Response** (200 OK):
```json
{
  "task_id": "uuid",
  "name": "string",
  "description": "string",
  "status": "in_progress",
  "priority": "high"
}
```

---

### Delete Task

Delete a task.

**Endpoint**: `DELETE /api/v1/tasks/{task_id}`

**Headers**:
- `Authorization`: Bearer token from login

**Response** (204 No Content)

---

## Automated Processes

### List Automated Processes

Get all automated processes.

**Endpoint**: `GET /api/v1/processes`

**Headers**:
- `Authorization`: Bearer token from login

**Response** (200 OK):
```json
{
  "processes": [
    {
      "process_id": "uuid",
      "name": "string",
      "description": "string",
      "trigger_type": "manual|time_based|event_based",
      "schedule": "0 9 * * *",
      "is_active": true,
      "last_execution": "2025-12-18T09:00:00Z"
    }
  ]
}
```

---

### Execute Process Manually

Trigger an automated process manually.

**Endpoint**: `POST /api/v1/processes/{process_id}/execute`

**Headers**:
- `Authorization`: Bearer token from login

**Response** (200 OK):
```json
{
  "execution_id": "uuid",
  "process_id": "uuid",
  "status": "success|failed|running",
  "message": "string",
  "started_at": "2025-12-18T10:00:00Z",
  "completed_at": "2025-12-18T10:05:00Z"
}
```

---

## Health Check

### Health Status

Check the API health status.

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-18T10:00:00Z"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error description"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required or invalid token"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Future versions may include:
- 100 requests per minute per user
- 1000 requests per hour per user

---

## WebSocket Support (Future)

Planned for real-time updates:
- Task status changes
- New messages in chat
- Process execution updates

**Endpoint**: `ws://localhost:8000/ws/{session_id}`

---

## API Versioning

The API uses URL-based versioning. Current version is `v1`.

Future versions will maintain backward compatibility or provide migration guides.

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/login",
    json={"username": "johndoe", "password": "securepass123"}
)
token = response.json()["token"]

# Create task
headers = {"Authorization": token}
response = requests.post(
    f"{BASE_URL}/api/v1/tasks",
    headers=headers,
    json={
        "name": "Review documentation",
        "description": "Check all API docs for accuracy",
        "priority": "high"
    }
)
task = response.json()
print(f"Created task: {task['task_id']}")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// Login
const loginResponse = await fetch(`${BASE_URL}/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "johndoe",
    password: "securepass123"
  })
});
const { token } = await loginResponse.json();

// Create task
const taskResponse = await fetch(`${BASE_URL}/api/v1/tasks`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": token
  },
  body: JSON.stringify({
    name: "Review documentation",
    description: "Check all API docs for accuracy",
    priority: "high"
  })
});
const task = await taskResponse.json();
console.log(`Created task: ${task.task_id}`);
```

---

## Postman Collection

A Postman collection is available for testing all API endpoints:

**Import URL**: `https://github.com/artaasd95/Behflow/blob/main/postman_collection.json`

---

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
