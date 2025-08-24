"""
TradingView Webhook Endpoint - Recebe dados reais do TradingView
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, Union
import logging
import json
from datetime import datetime
from services.pine_data_storage import store_pine_signal

logger = logging.getLogger(__name__)

router = APIRouter()

class TradingViewSignal(BaseModel):
    """Modelo para sinais do TradingView"""
    symbol: str
    timeframe: str
    timestamp: Union[int, str]
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        """Converte timestamp para string se for int"""
        if isinstance(v, int):
            return str(v)
        return v
    price: float
    
    # Indicadores técnicos reais
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    
    # Médias móveis
    sma_20: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # Volume e OHLC
    volume: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    
    # Sinais
    signal: Optional[str] = None  # BUY, SELL, HOLD
    confidence: Optional[float] = None
    
    # Dados adicionais
    alert_message: Optional[str] = None

# Armazenamento em memória dos dados recebidos
tradingview_data = {}

@router.post("/tradingview/webhook")
async def receive_tradingview_webhook(request: Request):
    """
    Endpoint para receber dados do TradingView via webhook
    """
    try:
        # Receber dados brutos
        raw_data = await request.body()
        logger.info(f"📡 TradingView webhook received: {len(raw_data)} bytes")
        
        # Parse JSON
        try:
            data = json.loads(raw_data.decode('utf-8'))
        except json.JSONDecodeError:
            # Tentar como form data
            form_data = await request.form()
            data = dict(form_data)
        
        logger.info(f"📊 TradingView data: {data}")
        
        # Validar dados mínimos
        if 'symbol' not in data or 'price' not in data:
            raise HTTPException(status_code=400, detail="Missing required fields: symbol, price")
        
        # Processar sinal
        signal_data = TradingViewSignal(
            symbol=data.get('symbol', '').upper(),
            timeframe=data.get('timeframe', '1h'),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            price=float(data.get('price', 0)),
            
            # Indicadores técnicos
            rsi=float(data.get('rsi')) if data.get('rsi') else None,
            macd=float(data.get('macd')) if data.get('macd') else None,
            macd_signal=float(data.get('macd_signal')) if data.get('macd_signal') else None,
            macd_histogram=float(data.get('macd_histogram')) if data.get('macd_histogram') else None,
            bb_upper=float(data.get('bb_upper')) if data.get('bb_upper') else None,
            bb_middle=float(data.get('bb_middle')) if data.get('bb_middle') else None,
            bb_lower=float(data.get('bb_lower')) if data.get('bb_lower') else None,
            
            # Médias móveis
            sma_20=float(data.get('sma_20')) if data.get('sma_20') else None,
            ema_12=float(data.get('ema_12')) if data.get('ema_12') else None,
            ema_26=float(data.get('ema_26')) if data.get('ema_26') else None,
            
            # OHLCV
            volume=float(data.get('volume')) if data.get('volume') else None,
            open=float(data.get('open')) if data.get('open') else None,
            high=float(data.get('high')) if data.get('high') else None,
            low=float(data.get('low')) if data.get('low') else None,
            close=float(data.get('close')) if data.get('close') else None,
            
            # Sinais
            signal=data.get('signal', 'HOLD').upper(),
            confidence=float(data.get('confidence', 50)),
            alert_message=data.get('alert_message', '')
        )
        
        # Integração com Gemini AI - ATIVADA
        ai_analysis = None
        try:
            from services.gemini_service import gemini_service
            ai_analysis = await gemini_service.analyze_crypto_signal(signal_data.dict())
            if ai_analysis:
                logger.info(f"🤖 Gemini AI analysis completed for {signal_data.symbol}")
            else:
                logger.warning(f"⚠️ Gemini AI returned no analysis for {signal_data.symbol}")
        except Exception as ai_error:
            logger.error(f"❌ Gemini AI analysis failed: {ai_error}")
        
        # Integração com sistema de alertas - ATIVADA
        try:
            from services.alert_system import alert_system
            from services.telegram_service import telegram_service
            from services.discord_service import DiscordService
            
            await alert_system.process_tradingview_signal(signal_data.dict(), ai_analysis)
            
            # Enviar alerta via Telegram se for sinal importante
            if signal_data.confidence and signal_data.confidence > 70:
                # Telegram Alert
                telegram_result = await telegram_service.send_technical_analysis_alert(
                    symbol=signal_data.symbol,
                    analysis_data={
                        'recommendation': signal_data.signal,
                        'confidence': signal_data.confidence,
                        'score': int(signal_data.confidence),  # Usar confidence como score
                        'signals': ['RSI Signal', 'MACD Signal', 'Bollinger Signal']
                    },
                    ai_recommendation=ai_analysis.get('analysis', '') if ai_analysis else None
                )
                if telegram_result.get('success'):
                    logger.info(f"📱 Telegram alert sent for {signal_data.symbol}")
                else:
                    logger.warning(f"⚠️ Telegram alert failed: {telegram_result.get('error')}")
                
                # Discord Alert
                discord_service = DiscordService()
                discord_result = await discord_service.send_technical_analysis_alert(
                    symbol=signal_data.symbol,
                    analysis_data={
                        'recommendation': signal_data.signal,
                        'confidence': signal_data.confidence,
                        'score': int(signal_data.confidence),
                        'signals': ['RSI Signal', 'MACD Signal', 'Bollinger Signal']
                    },
                    ai_recommendation=ai_analysis.get('analysis', '') if ai_analysis else None
                )
                if discord_result.get('success'):
                    logger.info(f"💬 Discord alert sent for {signal_data.symbol}")
                else:
                    logger.warning(f"⚠️ Discord alert failed: {discord_result.get('error')}")
            
            logger.info(f"🔔 Alert system processed signal for {signal_data.symbol}")
        except Exception as alert_error:
            logger.error(f"❌ Alert system failed: {alert_error}")
        
        # Armazenar dados por símbolo e timeframe
        key = f"{signal_data.symbol}_{signal_data.timeframe}"
        tradingview_data[key] = {
            "data": signal_data.dict(),
            "ai_analysis": ai_analysis,
            "received_at": datetime.now().isoformat(),
            "processed": True
        }
        
        # Armazenar no sistema global para análises
        store_pine_signal(signal_data.symbol, signal_data.dict())
        
        logger.info(f"✅ TradingView signal processed: {signal_data.symbol} - {signal_data.signal}")
        
        return {
            "status": "success",
            "message": f"Signal received for {signal_data.symbol}",
            "data": signal_data.dict(),
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"❌ TradingView webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/{symbol}")
async def get_tradingview_data(symbol: str, timeframe: str = "1h"):
    """
    Obter dados mais recentes do TradingView para um símbolo
    """
    try:
        key = f"{symbol.upper()}_{timeframe}"
        
        if key not in tradingview_data:
            raise HTTPException(status_code=404, detail=f"No TradingView data found for {symbol} {timeframe}")
        
        data = tradingview_data[key]
        
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "data": data["data"],
            "received_at": data["received_at"],
            "age_minutes": (datetime.now() - datetime.fromisoformat(data["received_at"])).total_seconds() / 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting TradingView data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_tradingview_status():
    """
    Status dos dados recebidos do TradingView
    """
    try:
        symbols = list(set([key.split('_')[0] for key in tradingview_data.keys()]))
        timeframes = list(set([key.split('_')[1] for key in tradingview_data.keys()]))
        
        recent_data = {}
        for key, data in tradingview_data.items():
            age_minutes = (datetime.now() - datetime.fromisoformat(data["received_at"])).total_seconds() / 60
            if age_minutes <= 60:  # Últimos 60 minutos
                recent_data[key] = {
                    "symbol": key.split('_')[0],
                    "timeframe": key.split('_')[1],
                    "age_minutes": round(age_minutes, 1),
                    "signal": data["data"].get("signal", "UNKNOWN"),
                    "price": data["data"].get("price", 0)
                }
        
        return {
            "status": "active" if recent_data else "inactive",
            "total_symbols": len(symbols),
            "symbols_tracked": symbols,
            "timeframes": timeframes,
            "recent_signals": len(recent_data),
            "recent_data": recent_data,
            "webhook_url": "/api/tradingview/webhook"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting TradingView status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/data/{symbol}")
async def clear_tradingview_data(symbol: str = None):
    """
    Limpar dados do TradingView
    """
    try:
        if symbol:
            # Limpar dados de um símbolo específico
            keys_to_remove = [key for key in tradingview_data.keys() if key.startswith(symbol.upper())]
            for key in keys_to_remove:
                del tradingview_data[key]
            return {"message": f"Cleared data for {symbol}", "keys_removed": len(keys_to_remove)}
        else:
            # Limpar todos os dados
            count = len(tradingview_data)
            tradingview_data.clear()
            return {"message": "Cleared all TradingView data", "keys_removed": count}
            
    except Exception as e:
        logger.error(f"❌ Error clearing TradingView data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

