"""
Endpoints para análises técnicas reais
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from services.gemini_service import gemini_service
from services.real_analysis_service import real_analysis_service
from services.coingecko_service import coingecko_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Mapeamento de símbolos
SYMBOL_TO_ID = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum', 
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'AVAX': 'avalanche-2',
    'DOT': 'polkadot',
    'LINK': 'chainlink',
    'UNI': 'uniswap'
}

@router.get("/analysis/technical/{symbol}")
async def get_technical_analysis(symbol: str, timeframe: str = "1h"):
    """
    Obter análise técnica REAL de uma criptomoeda
    """
    try:
        logger.info(f"📊 Iniciando análise técnica REAL de {symbol} ({timeframe})...")
        
        # Usar o serviço de análise REAL
        analysis_result = await real_analysis_service.analyze_symbol_complete(symbol, timeframe)
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        logger.info(f"✅ Análise técnica REAL de {symbol} concluída")
        
        return {
            "success": True,
            "data": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na análise técnica REAL de {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/analysis/overview")
async def get_analysis_overview():
    """
    Obter visão geral das análises técnicas dos principais símbolos
    """
    try:
        logger.info("📊 Carregando visão geral das análises...")
        
        analyses = []
        
        # Analisar os 5 principais símbolos
        main_symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA']
        
        for symbol in main_symbols:
            try:
                # Buscar análise de cada símbolo
                analysis_response = await get_technical_analysis(symbol)
                if analysis_response.get('success'):
                    analyses.append(analysis_response['data'])
                    
            except Exception as symbol_error:
                logger.warning(f"⚠️ Falha na análise de {symbol}: {symbol_error}")
                continue
        
        # Calcular estatísticas gerais
        total_analyses = len(analyses)
        buy_signals = len([a for a in analyses if a['recommendation'] == 'BUY'])
        sell_signals = len([a for a in analyses if a['recommendation'] == 'SELL'])
        hold_signals = len([a for a in analyses if a['recommendation'] == 'HOLD'])
        
        avg_score = sum([a['score'] for a in analyses]) / total_analyses if total_analyses > 0 else 0
        avg_confidence = sum([a['confidence'] for a in analyses]) / total_analyses if total_analyses > 0 else 0
        
        overview = {
            "total_analyses": total_analyses,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "hold_signals": hold_signals,
            "average_score": round(avg_score, 1),
            "average_confidence": round(avg_confidence, 1),
            "market_sentiment": "BULLISH" if buy_signals > sell_signals else "BEARISH" if sell_signals > buy_signals else "NEUTRAL",
            "analyses": analyses
        }
        
        logger.info(f"✅ Visão geral carregada: {total_analyses} análises, sentimento {overview['market_sentiment']}")
        
        return {
            "success": True,
            "data": overview,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar visão geral das análises: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/analysis/bulk")
async def get_bulk_analysis(symbols: List[str], timeframe: str = "1h"):
    """
    Obter análises técnicas em lote para múltiplos símbolos
    """
    try:
        logger.info(f"📊 Iniciando análise em lote de {len(symbols)} símbolos...")
        
        results = []
        
        for symbol in symbols:
            try:
                analysis_response = await get_technical_analysis(symbol, timeframe)
                if analysis_response.get('success'):
                    results.append(analysis_response['data'])
                    
            except Exception as symbol_error:
                logger.warning(f"⚠️ Falha na análise de {symbol}: {symbol_error}")
                # Adicionar resultado de erro
                results.append({
                    "symbol": symbol.upper(),
                    "error": str(symbol_error),
                    "success": False
                })
        
        logger.info(f"✅ Análise em lote concluída: {len(results)} resultados")
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na análise em lote: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

