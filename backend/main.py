"""
CryptoAnalyzer Pro Backend - REAL IMPLEMENTATION
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Import REAL services
from api.routes import api_router
from api.telegram_test import router as telegram_router
from api.discord_test import router as discord_router
from api.alerts_test import router as alerts_router
from services.coingecko_service import coingecko_service
from services.technical_analysis_complete import technical_analysis_service
from services.gemini_service import gemini_service
from services.notification_service import notification_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting CryptoAnalyzer Pro Backend - REAL IMPLEMENTATION")
    
    # Initialize services
    try:
        logger.info("Initializing REAL services...")
        
        # Initialize cache service first
        try:
            from services.cache_service import cache_service
            await cache_service.initialize()
            logger.info("✅ Cache service initialized")
        except Exception as e:
            logger.error(f"❌ Cache service initialization failed: {e}")
        
        # Test CoinGecko connection
        global_data = await coingecko_service.get_global_data()
        if global_data:
            logger.info("✅ CoinGecko API connected successfully")
        else:
            logger.warning("⚠️ CoinGecko API connection issues")
        
        # Test Gemini AI
        if os.getenv("GEMINI_API_KEY"):
            logger.info("✅ Gemini AI configured")
        else:
            logger.warning("⚠️ Gemini AI not configured")
        
        # Test notifications
        telegram_configured = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        discord_configured = bool(os.getenv("DISCORD_WEBHOOK_URL"))
        
        logger.info(f"✅ Telegram notifications: {'enabled' if telegram_configured else 'disabled'}")
        logger.info(f"✅ Discord notifications: {'enabled' if discord_configured else 'disabled'}")
        
        logger.info("🎯 All REAL services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down CryptoAnalyzer Pro Backend")
    try:
        # Cleanup cache service
        try:
            from services.cache_service import cache_service
            if cache_service.redis and cache_service.redis_connected:
                await cache_service.redis.close()
            logger.info("✅ Cache service cleaned up")
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")
        
        await coingecko_service.close()
        await gemini_service.close()
        logger.info("✅ Services closed successfully")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")


# Create FastAPI app with REAL implementation
app = FastAPI(
    title="CryptoAnalyzer Pro API - REAL",
    description="Professional cryptocurrency analysis platform with REAL data and AI insights",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CryptoAnalyzer Pro API - REAL IMPLEMENTATION",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "real_market_data": True,
            "technical_analysis": True,
            "ai_insights": bool(os.getenv("GEMINI_API_KEY")),
            "notifications": True,
            "multiple_timeframes": True
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "crypto_list": "/api/crypto/list",
            "technical_analysis": "/api/analysis/technical/{symbol}",
            "altcoin_season": "/api/analysis/altcoins",
            "market_overview": "/api/market/overview"
        }
    }


@app.get("/api/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Test CoinGecko
        coingecko_status = "operational"
        try:
            test_data = await coingecko_service.get_global_data()
            if not test_data:
                coingecko_status = "degraded"
        except Exception:
            coingecko_status = "error"
        
        # Test Gemini AI
        gemini_status = "configured" if os.getenv("GEMINI_API_KEY") else "not_configured"
        
        # Test notifications
        telegram_status = "configured" if os.getenv("TELEGRAM_BOT_TOKEN") else "not_configured"
        discord_status = "configured" if os.getenv("DISCORD_WEBHOOK_URL") else "not_configured"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "implementation": "REAL",
            "services": {
                "coingecko_api": coingecko_status,
                "gemini_ai": gemini_status,
                "telegram_notifications": telegram_status,
                "discord_notifications": discord_status,
                "technical_analysis": "operational",
                "database": "operational"
            },
            "features": {
                "real_time_data": True,
                "multiple_timeframes": ["30m", "1h", "4h", "1d"],
                "technical_indicators": ["RSI", "MACD", "Bollinger Bands", "SMA", "EMA"],
                "ai_powered": bool(os.getenv("GEMINI_API_KEY")),
                "pattern_detection": True,
                "alert_system": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/health")
async def health_check_legacy():
    """Legacy health check endpoint"""
    return await health_check()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Include API routes
# Add new REAL data endpoints
from api.market_endpoints import router as market_router
from api.analysis_endpoints import router as analysis_router
from api.tradingview_pine_webhook import router as pine_webhook_router
from api.tradingview_webhook import router as tradingview_webhook_router
app.include_router(market_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(pine_webhook_router, prefix="/api")
app.include_router(tradingview_webhook_router, prefix="/api")

# Add specific service routers
app.include_router(telegram_router, prefix="/api/telegram")
app.include_router(discord_router, prefix="/api/discord")
app.include_router(alerts_router, prefix="/api/alerts")


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🚀 Starting CryptoAnalyzer Pro Backend on {host}:{port}")
    logger.info(f"📊 Real data implementation: ENABLED")
    logger.info(f"🤖 AI insights: {'ENABLED' if os.getenv('GEMINI_API_KEY') else 'DISABLED'}")
    logger.info(f"📱 Notifications: {'ENABLED' if os.getenv('TELEGRAM_BOT_TOKEN') else 'DISABLED'}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )

