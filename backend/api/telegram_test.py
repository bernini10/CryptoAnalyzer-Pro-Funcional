"""
Telegram Test Endpoint
"""
from fastapi import APIRouter, HTTPException
from services.telegram_service import telegram_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test")
async def test_telegram_connection():
    """Test Telegram bot connection"""
    try:
        result = await telegram_service.send_test_message()
        
        if result.get('success'):
            return {
                "status": "success",
                "message": "Telegram bot connected successfully",
                "bot_info": {
                    "username": result.get('bot_username'),
                    "name": result.get('bot_name')
                }
            }
        else:
            return {
                "status": "error",
                "message": "Failed to connect to Telegram",
                "error": result.get('error')
            }
            
    except Exception as e:
        logger.error(f"Error testing Telegram: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-test-alert")
async def send_test_alert():
    """Send a test alert to Telegram"""
    try:
        # Test technical analysis alert
        result = await telegram_service.send_technical_analysis_alert(
            symbol="BTC",
            analysis_data={
                'recommendation': 'BUY',
                'confidence': 85,
                'score': 87,
                'signals': ['RSI Oversold', 'MACD Bullish Crossover', 'Volume Spike']
            },
            ai_recommendation="🤖 AI Analysis: Strong bullish momentum detected with RSI showing oversold conditions and MACD confirming upward trend. Consider entry on current levels with stop loss at $110,000."
        )
        
        if result.get('success'):
            return {
                "status": "success",
                "message": "Test alert sent successfully",
                "message_id": result.get('message_id')
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send test alert",
                "error": result.get('error')
            }
            
    except Exception as e:
        logger.error(f"Error sending test alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_telegram_status():
    """Get Telegram service status"""
    try:
        is_configured = telegram_service.is_configured()
        
        if is_configured:
            test_result = await telegram_service.send_test_message()
            return {
                "configured": True,
                "connected": test_result.get('success', False),
                "bot_info": {
                    "username": test_result.get('bot_username'),
                    "name": test_result.get('bot_name')
                } if test_result.get('success') else None,
                "error": test_result.get('error') if not test_result.get('success') else None
            }
        else:
            return {
                "configured": False,
                "connected": False,
                "error": "Telegram bot token not configured"
            }
            
    except Exception as e:
        logger.error(f"Error getting Telegram status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

