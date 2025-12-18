"""
FastAPI main application entry point
"""
from fastapi import FastAPI
from app.api.routers import chat, auth

app = FastAPI(title="Behflow API", version="0.1.0")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
