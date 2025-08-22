"""
API Routes for CryptoAnalyzer Pro
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import asyncio
import logging

from core.database import get_db, AsyncSession
from services.technical_analysis import TechnicalAnalysisService
from services.alert_system import AlertService

logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter()

# Initialize services
tech_analysis = TechnicalAnalysisService()
alert_service = AlertService()


@api_router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "service": "CryptoAnalyzer Pro API",
        "version": "1.0.0"
    }


@api_router.get("/crypto/list")
async def get_crypto_list(
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get list of cryptocurrencies"""
    try:
        # Mock data for now - replace with real API call
        mock_data = [
            {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 67500.0,
                "market_cap": 1320000000000,
                "price_change_24h": 2.4,
                "volume_24h": 28000000000
            },
            {
                "id": "ethereum",
                "symbol": "ETH", 
                "name": "Ethereum",
                "current_price": 4350.0,
                "market_cap": 523000000000,
                "price_change_24h": 3.1,
                "volume_24h": 15000000000
            },
            {
                "id": "uniswap",
                "symbol": "UNI",
                "name": "Uniswap",
                "current_price": 11.47,
                "market_cap": 8900000000,
                "price_change_24h": 8.7,
                "volume_24h": 245000000
            }
        ]
        
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        return {
            "data": mock_data[start_idx:end_idx],
            "total": len(mock_data),
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching crypto list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cryptocurrency data")


@api_router.get("/crypto/{symbol}")
async def get_crypto_details(symbol: str):
    """Get detailed information for a specific cryptocurrency"""
    try:
        # Mock data - replace with real API call
        mock_data = {
            "id": symbol.lower(),
            "symbol": symbol.upper(),
            "name": f"Cryptocurrency {symbol.upper()}",
            "current_price": 100.0,
            "market_cap": 1000000000,
            "price_change_24h": 2.5,
            "volume_24h": 50000000,
            "high_24h": 105.0,
            "low_24h": 95.0,
            "ath": 150.0,
            "atl": 10.0
        }
        
        return mock_data
        
    except Exception as e:
        logger.error(f"Error fetching crypto details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data for {symbol}")


@api_router.get("/analysis/technical/{symbol}")
async def get_technical_analysis(
    symbol: str,
    timeframe: str = Query("1d", regex="^(1m|5m|15m|1h|4h|1d|1w)$")
):
    """Get technical analysis for a cryptocurrency"""
    try:
        analysis = await tech_analysis.analyze_symbol(symbol, timeframe)
        return analysis
        
    except Exception as e:
        logger.error(f"Error in technical analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Technical analysis failed")


@api_router.get("/analysis/altcoins")
async def get_altcoin_analysis():
    """Get altcoin season analysis"""
    try:
        # Mock altcoin analysis data
        analysis = {
            "btc_dominance": 59.8,
            "alt_season_index": 67,
            "trend": "alt_season_starting",
            "top_altcoins": [
                {
                    "symbol": "UNI",
                    "score": 95,
                    "signals": ["Bollinger Squeeze", "Golden Cross", "Volume Spike"],
                    "recommendation": "buy",
                    "confidence": 0.85
                },
                {
                    "symbol": "ADA",
                    "score": 88,
                    "signals": ["Support Level", "RSI Oversold"],
                    "recommendation": "buy", 
                    "confidence": 0.78
                },
                {
                    "symbol": "TAO",
                    "score": 87,
                    "signals": ["AI Narrative", "Breakout Pattern"],
                    "recommendation": "buy",
                    "confidence": 0.82
                }
            ]
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in altcoin analysis: {e}")
        raise HTTPException(status_code=500, detail="Altcoin analysis failed")


@api_router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    """Get user alerts"""
    try:
        # Mock alerts data
        alerts = [
            {
                "id": "1",
                "symbol": "UNI",
                "type": "technical",
                "message": "Bollinger Bands squeeze detected",
                "timestamp": "2025-01-19T10:30:00Z",
                "priority": "high",
                "is_active": True
            },
            {
                "id": "2", 
                "symbol": "ADA",
                "type": "price",
                "message": "Price crossed above $0.50",
                "timestamp": "2025-01-19T10:25:00Z",
                "priority": "medium",
                "is_active": True
            }
        ]
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


@api_router.post("/alerts")
async def create_alert(
    alert_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Create a new alert"""
    try:
        # Validate required fields
        required_fields = ["symbol", "type", "condition", "target_value"]
        for field in required_fields:
            if field not in alert_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Mock alert creation
        new_alert = {
            "id": "new_alert_id",
            "symbol": alert_data["symbol"],
            "type": alert_data["type"],
            "condition": alert_data["condition"],
            "target_value": alert_data["target_value"],
            "is_active": True,
            "created_at": "2025-01-19T10:35:00Z"
        }
        
        return new_alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert")


@api_router.get("/dashboard")
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    """Get dashboard data"""
    try:
        dashboard_data = {
            "market_overview": {
                "total_market_cap": 2450000000000,
                "total_volume": 89000000000,
                "btc_dominance": 59.8,
                "active_cryptocurrencies": 26847
            },
            "portfolio_summary": {
                "total_value": 125000,
                "total_pnl": 15750,
                "total_pnl_percentage": 14.4,
                "best_performer": "UNI",
                "worst_performer": "ADA"
            },
            "recent_alerts": [
                {
                    "symbol": "UNI",
                    "message": "Bollinger Squeeze detected",
                    "timestamp": "2025-01-19T10:30:00Z",
                    "priority": "high"
                }
            ],
            "trending_coins": [
                {"symbol": "BTC", "name": "Bitcoin", "price": 67500, "change": 2.4},
                {"symbol": "ETH", "name": "Ethereum", "price": 4350, "change": 3.1},
                {"symbol": "UNI", "name": "Uniswap", "price": 11.47, "change": 8.7}
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")


@api_router.get("/portfolio")
async def get_portfolios(db: AsyncSession = Depends(get_db)):
    """Get user portfolios"""
    try:
        # Mock portfolio data
        portfolios = [
            {
                "id": "portfolio_1",
                "name": "Main Portfolio",
                "total_value": 125000,
                "total_pnl": 15750,
                "total_pnl_percentage": 14.4,
                "holdings": [
                    {
                        "symbol": "BTC",
                        "quantity": 1.5,
                        "average_cost": 45000,
                        "current_price": 67500,
                        "pnl": 33750,
                        "pnl_percentage": 50.0
                    },
                    {
                        "symbol": "ETH", 
                        "quantity": 10.0,
                        "average_cost": 3000,
                        "current_price": 4350,
                        "pnl": 13500,
                        "pnl_percentage": 45.0
                    }
                ]
            }
        ]
        
        return portfolios
        
    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolios")

