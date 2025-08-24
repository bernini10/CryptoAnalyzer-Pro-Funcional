"""
Alerts Test Endpoint
"""
from fastapi import APIRouter, HTTPException
from services.alert_system import alert_system
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/status")
async def get_alerts_status():
    """Get alerts system status"""
    try:
        status = await alert_system.get_system_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting alerts status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-monitoring")
async def start_monitoring():
    """Start automatic monitoring"""
    try:
        if alert_system.running:
            return {
                "status": "info",
                "message": "Alert system is already running"
            }
        
        # Start monitoring in background
        import asyncio
        asyncio.create_task(alert_system.start_monitoring())
        
        return {
            "status": "success",
            "message": "Alert monitoring started"
        }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-monitoring")
async def stop_monitoring():
    """Stop automatic monitoring"""
    try:
        await alert_system.stop_monitoring()
        return {
            "status": "success",
            "message": "Alert monitoring stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-price-alert")
async def test_price_alert():
    """Send a test price alert"""
    try:
        # Simulate price alert data
        alert_data = {
            'price': 115000.50,
            'change_24h': 5.2,
            'market_cap': 2200000000000,
            'volume_24h': 45000000000
        }
        
        results = await alert_system._send_alert("price_change", "BTC", alert_data)
        
        return {
            "status": "success",
            "message": "Test price alert sent",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error sending test price alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-technical-alert")
async def test_technical_alert():
    """Send a test technical analysis alert"""
    try:
        # Simulate technical analysis data
        alert_data = {
            'analysis': {
                'symbol': 'BTC',
                'recommendation': 'BUY',
                'confidence': 87,
                'score': 89,
                'signals': ['RSI Oversold', 'MACD Bullish Crossover', 'Volume Spike', 'BB Breakout Up'],
                'indicators': {
                    'rsi': 28.5,
                    'macd': 0.15,
                    'bb_position': 'Breakout Up'
                }
            },
            'ai_recommendation': '🤖 **AI Analysis:** Strong bullish momentum detected with multiple technical indicators aligning. RSI shows oversold conditions presenting a potential buying opportunity. MACD confirms upward trend with bullish crossover. Volume spike indicates institutional interest. Recommended entry with stop loss at $110,000.',
            'reasons': ['Test Alert', 'Multiple Bullish Signals', 'High Confidence']
        }
        
        results = await alert_system._send_alert("technical_analysis", "BTC", alert_data)
        
        return {
            "status": "success",
            "message": "Test technical alert sent",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error sending test technical alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-altseason-alert")
async def test_altseason_alert():
    """Send a test altseason alert"""
    try:
        # Simulate altseason data
        alert_data = {
            'altseason_index': 72.5,
            'bitcoin_dominance': 45.2,
            'status': 'Strong Alt Season',
            'top_altcoins': [
                {'symbol': 'ETH', 'vs_btc_7d': 8.5},
                {'symbol': 'SOL', 'vs_btc_7d': 12.3},
                {'symbol': 'ADA', 'vs_btc_7d': 6.7},
                {'symbol': 'AVAX', 'vs_btc_7d': 9.1},
                {'symbol': 'DOT', 'vs_btc_7d': 5.4}
            ]
        }
        
        results = await alert_system._send_alert("altseason", "ALTSEASON", alert_data)
        
        return {
            "status": "success",
            "message": "Test altseason alert sent",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error sending test altseason alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-all-systems")
async def test_all_systems():
    """Test all alert systems"""
    try:
        results = {}
        
        # Test technical alert
        tech_result = await test_technical_alert()
        results['technical'] = tech_result
        
        # Wait a bit
        import asyncio
        await asyncio.sleep(2)
        
        # Test price alert
        price_result = await test_price_alert()
        results['price'] = price_result
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test altseason alert
        alt_result = await test_altseason_alert()
        results['altseason'] = alt_result
        
        return {
            "status": "success",
            "message": "All alert systems tested",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error testing all systems: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cooldowns")
async def get_cooldowns():
    """Get current cooldowns"""
    try:
        from datetime import datetime
        
        cooldowns = {}
        for alert_key, last_time in alert_system.last_alerts.items():
            time_since = datetime.now() - last_time
            remaining = (alert_system.alert_cooldown_minutes * 60) - time_since.total_seconds()
            
            if remaining > 0:
                cooldowns[alert_key] = {
                    'last_sent': last_time.isoformat(),
                    'remaining_seconds': int(remaining),
                    'remaining_minutes': round(remaining / 60, 1)
                }
        
        return {
            "status": "success",
            "active_cooldowns": cooldowns,
            "total_cooldowns": len(cooldowns)
        }
    except Exception as e:
        logger.error(f"Error getting cooldowns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

