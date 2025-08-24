"""
Webhook para receber dados REAIS do Pine Script do TradingView
Recebe indicadores técnicos calculados diretamente no TradingView Premium
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Modelo para dados do Pine Script
class PineScriptData(BaseModel):
    symbol: str
    price: float
    timestamp: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    volume: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    close: Optional[float] = None

# Armazenamento em memória dos dados recebidos
pine_data_storage = {}

@router.post("/tradingview/pine-webhook")
async def receive_pine_data(data: PineScriptData):
    """
    Receber dados REAIS do Pine Script do TradingView
    """
    try:
        logger.info(f"📊 Recebendo dados REAIS do Pine Script: {data.symbol} - ${data.price}")
        
        # Processar dados recebidos
        processed_data = {
            'symbol': data.symbol.replace('USDT', '').replace('USD', ''),  # BTC, ETH, etc.
            'price': data.price,
            'timestamp': data.timestamp,
            'technical_indicators': {
                'rsi': data.rsi,
                'macd': {
                    'macd': data.macd,
                    'signal': data.macd_signal,
                    'histogram': data.macd_histogram
                } if data.macd is not None else None,
                'bollinger_bands': {
                    'upper': data.bb_upper,
                    'middle': data.bb_middle,
                    'lower': data.bb_lower
                } if data.bb_upper is not None else None,
                'sma_20': data.sma_20,
                'sma_50': data.sma_50,
                'ema_12': data.ema_12,
                'ema_26': data.ema_26
            },
            'ohlcv': {
                'open': data.open,
                'high': data.high,
                'low': data.low,
                'close': data.close,
                'volume': data.volume
            },
            'data_source': 'TradingView Pine Script REAL',
            'data_quality': 'REAL',
            'received_at': datetime.now().isoformat()
        }
        
        # Armazenar dados
        symbol = processed_data['symbol']
        pine_data_storage[symbol] = processed_data
        
        logger.info(f"✅ Dados REAIS armazenados para {symbol}: RSI {data.rsi}, MACD {data.macd}")
        
        return {
            "success": True,
            "message": f"Dados REAIS recebidos para {symbol}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar dados do Pine Script: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/tradingview/pine-data/{symbol}")
async def get_pine_data(symbol: str):
    """
    Obter dados REAIS recebidos do Pine Script
    """
    try:
        symbol = symbol.upper()
        
        if symbol not in pine_data_storage:
            raise HTTPException(status_code=404, detail=f"Dados não encontrados para {symbol}")
        
        data = pine_data_storage[symbol]
        
        logger.info(f"📊 Retornando dados REAIS do Pine Script para {symbol}")
        
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados do Pine Script: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/tradingview/pine-status")
async def get_pine_status():
    """
    Status dos dados recebidos do Pine Script
    """
    try:
        symbols_count = len(pine_data_storage)
        latest_updates = {}
        
        for symbol, data in pine_data_storage.items():
            latest_updates[symbol] = {
                'price': data['price'],
                'received_at': data['received_at'],
                'has_rsi': data['technical_indicators']['rsi'] is not None,
                'has_macd': data['technical_indicators']['macd'] is not None,
                'has_bollinger': data['technical_indicators']['bollinger_bands'] is not None
            }
        
        return {
            "success": True,
            "status": "operational",
            "symbols_tracked": symbols_count,
            "latest_updates": latest_updates,
            "data_source": "TradingView Pine Script REAL",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status do Pine Script: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/tradingview/pine-webhook-raw")
async def receive_pine_data_raw(request: Request):
    """
    Webhook raw para debugging - aceita qualquer formato
    """
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "")
        
        logger.info(f"📨 Webhook raw recebido - Content-Type: {content_type}")
        logger.info(f"📨 Body: {body.decode('utf-8')[:500]}...")  # Primeiros 500 chars
        
        # Tentar parsear JSON
        if "application/json" in content_type:
            data = await request.json()
            logger.info(f"📊 JSON parsed: {data}")
        else:
            data = body.decode('utf-8')
        
        return {
            "success": True,
            "message": "Webhook raw recebido",
            "content_type": content_type,
            "data_preview": str(data)[:200],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook raw: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Função para obter dados do Pine Script (para usar em outros serviços)
def get_pine_script_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Obter dados do Pine Script para uso interno
    """
    symbol = symbol.upper()
    return pine_data_storage.get(symbol)

