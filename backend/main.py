"""
CryptoAnalyzer Pro - Main FastAPI Application
Fixed version with correct structure and imports
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Local imports with correct structure
from core.config import settings
from core.database import engine, Base
from api.routes import api_router
from services.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting CryptoAnalyzer Pro...")
    
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
        
        # Start background scheduler
        await start_scheduler()
        logger.info("✅ Background scheduler started")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🛑 Shutting down CryptoAnalyzer Pro...")
        await stop_scheduler()
        logger.info("✅ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title="CryptoAnalyzer Pro API",
    description="Advanced cryptocurrency analysis and trading platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "CryptoAnalyzer Pro API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

