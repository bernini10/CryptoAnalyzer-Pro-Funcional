"""
Discord Test Endpoint
"""
from fastapi import APIRouter, HTTPException
from services.discord_service import DiscordService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test")
async def test_discord_connection():
    """Test Discord webhook connection"""
    try:
        discord_service = DiscordService()
        result = await discord_service.send_test_message()
        
        if result.get('success'):
            return {
                "status": "success",
                "message": "Discord webhook connected successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to connect to Discord",
                "error": result.get('error')
            }
            
    except Exception as e:
        logger.error(f"Error testing Discord: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-test-alert")
async def send_test_alert():
    """Send a test alert to Discord"""
    try:
        discord_service = DiscordService()
        
        # Test technical analysis alert
        result = await discord_service.send_technical_analysis_alert(
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
                "message": "Test alert sent successfully to Discord"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send test alert to Discord",
                "error": result.get('error')
            }
            
    except Exception as e:
        logger.error(f"Error sending test alert to Discord: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_discord_status():
    """Get Discord service status"""
    try:
        discord_service = DiscordService()
        is_configured = discord_service.is_configured()
        
        if is_configured:
            test_result = await discord_service.send_test_message()
            return {
                "configured": True,
                "connected": test_result.get('success', False),
                "webhook_url": discord_service.webhook_url[:50] + "..." if discord_service.webhook_url else None,
                "error": test_result.get('error') if not test_result.get('success') else None
            }
        else:
            return {
                "configured": False,
                "connected": False,
                "error": "Discord webhook URL not configured"
            }
            
    except Exception as e:
        logger.error(f"Error getting Discord status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

