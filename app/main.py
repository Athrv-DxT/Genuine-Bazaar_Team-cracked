"""
Main FastAPI application for Retail Cortex
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import auth, alerts, keywords, trends, location

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered retail intelligence platform for demand peak detection and promotion timing",
    version=settings.app_version,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(keywords.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(location.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    import logging
    logger = logging.getLogger(__name__)
    # Start background scheduler
    from app.scheduler import start_scheduler
    start_scheduler()
    logger.info("Retail Cortex API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    import logging
    logger = logging.getLogger(__name__)
    from app.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("Retail Cortex API shutting down")


if __name__ == "__main__":
    import uvicorn
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    uvicorn.run(app, host="0.0.0.0", port=8000)
