from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import database setup
from data.database import create_db_and_tables
from data.models import *

# Import routers
from backend.api import campaigns, schedules, agents

# Import scheduler
from backend.core.scheduler import scheduler, start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("Starting up...")
    create_db_and_tables()
    start_scheduler()
    yield
    # Shutdown
    print("Shutting down...")
    scheduler.shutdown()

# Create FastAPI app
app = FastAPI(
    title="BizHacks Campaign Manager",
    description="Agentic Marketing Campaign Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/")
async def root():
    return {"message": "BizHacks Campaign Manager API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Set to False in production
    )