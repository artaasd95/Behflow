"""
FastAPI main application entry point
"""
from fastapi import FastAPI
from app.api.routers import chat, auth
from shared.logger import get_logger
from contextlib import asynccontextmanager
from typing import AsyncIterator

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Behflow API")
    try:
        yield
    finally:
        logger.info("Shutting down Behflow API")

app = FastAPI(title="Behflow API", version="0.1.0", lifespan=lifespan)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy"}
