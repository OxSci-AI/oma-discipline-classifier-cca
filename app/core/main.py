"""
FastAPI Application Entry Point for Discipline Classifier Agent
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from oxsci_oma_core.scheduler import TaskScheduler

from app.core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Import agents after app is created
    from app.agents import DisciplineClassifierCCA

    # Initialize task scheduler without adapter
    scheduler = TaskScheduler(adapter_class=None)

    # Register discipline classifier agent
    scheduler.register_agent(DisciplineClassifierCCA)

    # Start scheduler
    await scheduler.start()

    yield

    # Cleanup on shutdown
    await scheduler.stop()


# Create FastAPI app
app = FastAPI(
    title=config.SERVICE_NAME,
    description="OMA Discipline Classifier CCA Service",
    version=config.VERSION,
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": config.SERVICE_NAME,
        "version": config.VERSION,
    }
