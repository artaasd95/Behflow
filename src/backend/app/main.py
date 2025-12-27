"""
FastAPI main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import chat, auth, tasks
from app.scheduler import start_scheduler, shutdown_scheduler
from app.database.init_automated_processes import initialize_automated_processes
from shared.logger import get_logger
from contextlib import asynccontextmanager
from typing import AsyncIterator

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Behflow API")
    
    # Initialize automated processes in database
    try:
        initialize_automated_processes()
    except Exception as e:
        logger.error(f"Failed to initialize automated processes: {e}")
    
    # Start the scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
    
    try:
        yield
    finally:
        logger.info("Shutting down Behflow API")
        
        # Shutdown the scheduler
        try:
            shutdown_scheduler()
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")

app = FastAPI(title="Behflow API", version="0.1.0", lifespan=lifespan)

# Configure CORS
# For development, allow any frontend origin. NOTE: this is insecure for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev/testing
    allow_credentials=False,  # disable credentials to allow wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy"}
