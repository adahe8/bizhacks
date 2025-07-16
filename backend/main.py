# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict

from backend.core.config import settings
from backend.core.scheduler import scheduler
from data.database import init_db
from api import campaigns, schedules, agents, setup, metrics, gamestate
from external_apis.mock_media import router as mock_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting BizHacks Marketing Platform...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(setup.router, prefix="/api/setup", tags=["setup"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(gamestate.router, prefix="/api/gamestate", tags=["gamestate"])

# Include mock endpoints for development
app.include_router(mock_router, prefix="/mock", tags=["mock"])

@app.get("/")
def read_root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "Welcome to BizHacks Marketing Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )