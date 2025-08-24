"""
Real Technical Analysis Service - 100% DADOS REAIS
Usa Binance API para dados OHLCV e cálculos matemáticos reais
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from services.coingecko_ohlcv_service import coingecko_ohlcv_service
from services.real_technical_indicators import real_indicators

logger = logging.getLogger(__name__)

class RealTechnicalAnalysisService:
    """
    Serviço de análise técnica com dados 100% REAIS
    - Dados OHLCV da Binance API
    - Cálculos matemáticos reais de RSI, MACD, Bollinger Bands
    - Sinais detectados por algoritmos matemáticos
    - Scores baseados em análise técnica real
    """
    
    def __init__(self):
        self.cache = {}  # Cache simples para dados
        self.cache_ttl = 300  # 5 minutos
    
    async def analyze_symbol_real(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
        """
        Análise técnica 100% REAL de um símbolo
        
        Args:
            symbol: Símbolo da crypto (BTC, ETH, etc.)
            timeframe: Timeframe ('30m', '1h', '4h', '1d')
        
        Returns:
            Dict com análise técnica completa REAL
        """
        try:
            logger.info(f"🔍 Starting REAL analysis for {symbol} {timeframe}")
            
            # Mapear timeframes
            interval_map = {
                '30m': '1h',  # CoinGecko não tem 30m, usar 1h
                '1h': '1h', 
                '4h': '4h',
                '1d': '1d'
            }
            interval = interval_map.get(timeframe, '1h')
            
            # Obter dados OHLCV reais da CoinGecko
            df = await coingecko_ohlcv_service.get_ohlcv_dataframe(symbol, interval, 200)
            
            if df.empty:
                logger.warning(f"⚠️ No OHLCV data for {symbol}")
                return self._get_fallback_analysis(symbol, timeframe)
            
            logger.info(f"✅ Got {len(df)} real candles for {symbol} from CoinGecko")
            
            # Calcular indicadores técnicos REAIS
            prices = df['close']
            
            # RSI Real
            rsi = real_indicators.calculate_rsi(prices, period=14)
            current_rsi = rsi.iloc[-1]
            
            # MACD Real
            macd_data = real_indicators.calculate_macd(prices, fast=12, slow=26, signal=9)
            current_macd = macd_data['macd'].iloc[-1]
            current_signal = macd_data['signal'].iloc[-1]
            
            # Bollinger Bands Real
            bb_data = real_indicators.calculate_bollinger_bands(prices, period=20, std_dev=2.0)
            
            # SMA e EMA Real
            sma_20 = real_indicators.calculate_sma(prices, 20)
            ema_20 = real_indicators.calculate_ema(prices, 20)
            
            # Detectar sinais REAIS
            signals = real_indicators.detect_signals(df, rsi, macd_data, bb_data)
            
            # Calcular score e recomendação REAIS
            score, recommendation, confidence = real_indicators.calculate_score_and_recommendation(
                df, rsi, macd_data, bb_data, signals
            )
            
            # Análise de volume REAL
            current_volume = df['volume'].iloc[-1]
            avg_volume_20 = df['volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
            
            # Preços atuais REAIS
            current_price = df['close'].iloc[-1]
            high_24h = df['high'].tail(24).max() if len(df) >= 24 else df['high'].max()
            low_24h = df['low'].tail(24).min() if len(df) >= 24 else df['low'].min()
            
            # Determinar status dos indicadores
            rsi_status = self._get_rsi_status(current_rsi)
            macd_status = self._get_macd_status(current_macd, current_signal)
            bb_status = self._get_bb_status(current_price, bb_data)
            volume_status = self._get_volume_status(volume_ratio)
            
            # Resultado da análise REAL
            result = {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "data_source": "CoinGecko API - REAL OHLCV DATA",
                "candles_analyzed": len(df),
                
                # Recomendação REAL
                "recommendation": recommendation,
                "score": score,
                "confidence": round(confidence, 1),
                
                # Indicadores técnicos REAIS
                "indicators": {
                    "rsi": {
                        "value": round(current_rsi, 2),
                        "status": rsi_status,
                        "period": 14
                    },
                    "macd": {
                        "macd": round(current_macd, 6),
                        "signal": round(current_signal, 6),
                        "histogram": round(macd_data['histogram'].iloc[-1], 6),
                        "status": macd_status
                    },
                    "bollinger_bands": {
                        "upper": round(bb_data['upper'].iloc[-1], 2),
                        "middle": round(bb_data['middle'].iloc[-1], 2),
                        "lower": round(bb_data['lower'].iloc[-1], 2),
                        "status": bb_status,
                        "position": round(((current_price - bb_data['lower'].iloc[-1]) / 
                                        (bb_data['upper'].iloc[-1] - bb_data['lower'].iloc[-1])) * 100, 1)
                    },
                    "moving_averages": {
                        "sma_20": round(sma_20.iloc[-1], 2),
                        "ema_20": round(ema_20.iloc[-1], 2),
                        "price_vs_sma": "Above" if current_price > sma_20.iloc[-1] else "Below",
                        "price_vs_ema": "Above" if current_price > ema_20.iloc[-1] else "Below"
                    }
                },
                
                # Dados de preço REAIS
                "price_data": {
                    "current": round(current_price, 6),
                    "high_24h": round(high_24h, 6),
                    "low_24h": round(low_24h, 6),
                    "change_24h_pct": round(((current_price - df['close'].iloc[-24]) / df['close'].iloc[-24] * 100) if len(df) >= 24 else 0, 2)
                },
                
                # Volume REAL
                "volume_analysis": {
                    "current": round(current_volume, 2),
                    "average_20": round(avg_volume_20, 2),
                    "ratio": round(volume_ratio, 2),
                    "status": volume_status
                },
                
                # Sinais detectados REAIS
                "signals": signals,
                "signals_count": len(signals),
                
                # Metadados
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_quality": "REAL",
                "last_candle_time": df['timestamp'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"✅ REAL analysis completed for {symbol}: {recommendation} ({score}/100, {confidence:.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Real analysis error for {symbol}: {e}")
            return self._get_fallback_analysis(symbol, timeframe)
    
    def _get_rsi_status(self, rsi: float) -> str:
        """Determina status do RSI"""
        if rsi < 30:
            return "Oversold"
        elif rsi > 70:
            return "Overbought"
        elif rsi < 40:
            return "Bearish"
        elif rsi > 60:
            return "Bullish"
        else:
            return "Neutral"
    
    def _get_macd_status(self, macd: float, signal: float) -> str:
        """Determina status do MACD"""
        if macd > signal:
            if macd > 0:
                return "Strong Bullish"
            else:
                return "Bullish"
        else:
            if macd < 0:
                return "Strong Bearish"
            else:
                return "Bearish"
    
    def _get_bb_status(self, price: float, bb_data: Dict) -> str:
        """Determina status das Bollinger Bands"""
        upper = bb_data['upper'].iloc[-1]
        middle = bb_data['middle'].iloc[-1]
        lower = bb_data['lower'].iloc[-1]
        
        if price > upper:
            return "Above Upper Band"
        elif price < lower:
            return "Below Lower Band"
        elif price > middle:
            return "Above Middle"
        else:
            return "Below Middle"
    
    def _get_volume_status(self, ratio: float) -> str:
        """Determina status do volume"""
        if ratio > 2.0:
            return "Very High"
        elif ratio > 1.5:
            return "High"
        elif ratio > 0.8:
            return "Normal"
        elif ratio > 0.5:
            return "Low"
        else:
            return "Very Low"
    
    def _get_fallback_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Análise de fallback quando não há dados da Binance"""
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Fallback - No Real Data Available",
            "error": "Unable to fetch real data from CoinGecko API",
            "recommendation": "HOLD",
            "score": 50,
            "confidence": 30.0,
            "indicators": {
                "rsi": {"value": 50, "status": "Unknown"},
                "macd": {"status": "Unknown"},
                "bollinger_bands": {"status": "Unknown"}
            },
            "signals": ["No Real Data Available"],
            "data_quality": "FALLBACK"
        }

# Global instance
real_technical_analysis = RealTechnicalAnalysisService()

