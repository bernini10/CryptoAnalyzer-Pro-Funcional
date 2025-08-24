"""
Real Technical Analysis Service for CryptoAnalyzer Pro
Complete implementation with multiple timeframes and indicators
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
from scipy.signal import find_peaks

from .coingecko_service import coingecko_service

logger = logging.getLogger(__name__)


class RealTechnicalAnalysisService:
    """Real technical analysis service with comprehensive indicators"""
    
    def __init__(self):
        self.session = None
        self.timeframes = {
            "30m": 30,
            "1h": 60, 
            "4h": 240,
            "1d": 1440
        }
    
    async def comprehensive_analysis(self, symbol: str, timeframes: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive technical analysis across multiple timeframes"""
        if timeframes is None:
            timeframes = ["30m", "1h", "4h", "1d"]
        
        try:
            logger.info(f"Starting comprehensive analysis for {symbol}")
            
            # Get historical data for all timeframes
            timeframe_data = {}
            for tf in timeframes:
                try:
                    data = await self._get_historical_data(symbol, tf)
                    if data is not None and len(data) > 0:
                        timeframe_data[tf] = data
                        logger.info(f"Got {len(data)} data points for {symbol} {tf}")
                    else:
                        logger.warning(f"No data for {symbol} {tf}")
                except Exception as e:
                    logger.error(f"Error getting data for {symbol} {tf}: {e}")
            
            if not timeframe_data:
                logger.error(f"No data available for {symbol}")
                return self._generate_fallback_analysis(symbol)
            
            # Analyze each timeframe
            timeframe_analysis = {}
            for tf, data in timeframe_data.items():
                try:
                    analysis = await self._analyze_timeframe(symbol, data, tf)
                    timeframe_analysis[tf] = analysis
                    logger.info(f"Completed analysis for {symbol} {tf}")
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} {tf}: {e}")
            
            # Generate overall recommendation
            overall = self._generate_overall_recommendation(timeframe_analysis)
            
            return {
                "symbol": symbol.upper(),
                "timeframe_analysis": timeframe_analysis,
                "overall_recommendation": overall["recommendation"],
                "overall_score": overall["score"],
                "overall_confidence": overall["confidence"],
                "key_signals": overall["signals"],
                "risk_level": overall["risk_level"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            return self._generate_fallback_analysis(symbol)
    
    async def _get_historical_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get historical price data for analysis"""
        try:
            # Map symbol to CoinGecko ID if needed
            coin_id = await self._get_coin_id(symbol)
            if not coin_id:
                return None
            
            # Get appropriate number of days based on timeframe
            if timeframe == "30m":
                days = 7  # 7 days of 30min data
            elif timeframe == "1h":
                days = 14  # 14 days of hourly data  
            elif timeframe == "4h":
                days = 60  # 60 days of 4h data
            else:  # 1d
                days = 365  # 1 year of daily data
            
            # Get historical data from CoinGecko
            historical_data = await coingecko_service.get_historical_data(coin_id, days, "hourly")
            
            if not historical_data:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            
            if len(df) < 20:  # Need minimum data for analysis
                return None
            
            # Ensure required columns
            if 'price' not in df.columns:
                if 'prices' in df.columns:
                    df['price'] = df['prices']
                else:
                    return None
            
            # Add volume if not present
            if 'volume' not in df.columns:
                df['volume'] = 1000000  # Default volume
            
            return df.tail(200)  # Use last 200 data points
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol} {timeframe}: {e}")
            return None
    
    async def _get_coin_id(self, symbol: str) -> Optional[str]:
        """Map symbol to CoinGecko coin ID"""
        symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "BNB": "binancecoin",
            "ADA": "cardano",
            "SOL": "solana",
            "XRP": "ripple",
            "DOT": "polkadot",
            "DOGE": "dogecoin",
            "AVAX": "avalanche-2",
            "LINK": "chainlink",
            "MATIC": "matic-network",
            "UNI": "uniswap",
            "LTC": "litecoin",
            "ATOM": "cosmos",
            "FIL": "filecoin",
            "VET": "vechain",
            "ICP": "internet-computer",
            "HBAR": "hedera-hashgraph",
            "SAND": "the-sandbox",
            "MANA": "decentraland",
            "THETA": "theta-token"
        }
        
        return symbol_map.get(symbol.upper(), symbol.lower())
    
    async def _analyze_timeframe(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Analyze single timeframe"""
        try:
            prices = df['price'].values
            volumes = df['volume'].values if 'volume' in df.columns else np.ones(len(prices))
            
            # Calculate all indicators
            indicators = {
                "rsi": self._calculate_rsi(prices),
                "macd": self._calculate_macd(prices),
                "bollinger": self._calculate_bollinger_bands(prices),
                "sma_20": self._calculate_sma(prices, 20),
                "sma_50": self._calculate_sma(prices, 50),
                "ema_12": self._calculate_ema(prices, 12),
                "ema_26": self._calculate_ema(prices, 26),
                "stochastic": self._calculate_stochastic(df),
                "williams_r": self._calculate_williams_r(df),
                "volume_ratio": self._calculate_volume_ratio(volumes)
            }
            
            # Detect patterns and signals
            patterns = self._detect_patterns(prices, indicators)
            signals = self._generate_signals(indicators, patterns)
            
            # Calculate score and recommendation
            score = self._calculate_technical_score(indicators, signals)
            recommendation = self._get_recommendation(score, signals)
            confidence = self._calculate_confidence(indicators, signals)
            
            return {
                "timeframe": timeframe,
                "current_price": float(prices[-1]),
                "indicators": {
                    "rsi": float(indicators["rsi"][-1]),
                    "macd": float(indicators["macd"]["macd"][-1]),
                    "macd_signal": float(indicators["macd"]["signal"][-1]),
                    "bollinger_position": self._get_bollinger_position(prices[-1], indicators["bollinger"]),
                    "sma_20": float(indicators["sma_20"][-1]),
                    "sma_50": float(indicators["sma_50"][-1]),
                    "volume_ratio": float(indicators["volume_ratio"])
                },
                "patterns": patterns,
                "signals": signals,
                "recommendation": recommendation,
                "score": score,
                "confidence": confidence,
                "support_levels": self._find_support_levels(prices),
                "resistance_levels": self._find_resistance_levels(prices)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timeframe {timeframe}: {e}")
            return {
                "timeframe": timeframe,
                "error": str(e),
                "recommendation": "HOLD",
                "score": 50,
                "confidence": 0.3
            }
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI"""
        try:
            if len(prices) < period + 1:
                return np.array([50.0] * len(prices))
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            rsi_values = []
            
            for i in range(period, len(prices)):
                if i == period:
                    current_avg_gain = avg_gain
                    current_avg_loss = avg_loss
                else:
                    current_avg_gain = (current_avg_gain * (period - 1) + gains[i-1]) / period
                    current_avg_loss = (current_avg_loss * (period - 1) + losses[i-1]) / period
                
                if current_avg_loss == 0:
                    rsi = 100.0
                else:
                    rs = current_avg_gain / current_avg_loss
                    rsi = 100.0 - (100.0 / (1.0 + rs))
                
                rsi_values.append(rsi)
            
            result = np.array([50.0] * period + rsi_values)
            return result
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return np.array([50.0] * len(prices))
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, np.ndarray]:
        """Calculate MACD"""
        try:
            if len(prices) < slow:
                return {
                    'macd': np.array([0.0] * len(prices)),
                    'signal': np.array([0.0] * len(prices)),
                    'histogram': np.array([0.0] * len(prices))
                }
            
            ema_fast = self._calculate_ema(prices, fast)
            ema_slow = self._calculate_ema(prices, slow)
            
            macd_line = ema_fast - ema_slow
            signal_line = self._calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {
                'macd': np.array([0.0] * len(prices)),
                'signal': np.array([0.0] * len(prices)),
                'histogram': np.array([0.0] * len(prices))
            }
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2) -> Dict[str, np.ndarray]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                return {
                    'upper': prices.copy(),
                    'middle': prices.copy(),
                    'lower': prices.copy()
                }
            
            middle = self._calculate_sma(prices, period)
            
            std_values = []
            for i in range(len(prices)):
                if i < period - 1:
                    std_values.append(0.0)
                else:
                    window = prices[i - period + 1:i + 1]
                    std_values.append(np.std(window))
            
            std_array = np.array(std_values)
            
            upper = middle + (std_array * std_dev)
            lower = middle - (std_array * std_dev)
            
            return {
                'upper': upper,
                'middle': middle,
                'lower': lower
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {
                'upper': prices.copy(),
                'middle': prices.copy(),
                'lower': prices.copy()
            }
    
    def _calculate_sma(self, values: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average"""
        try:
            if len(values) < period:
                return values.copy()
            
            sma_values = []
            for i in range(len(values)):
                if i < period - 1:
                    sma_values.append(values[i])
                else:
                    window = values[i - period + 1:i + 1]
                    sma_values.append(np.mean(window))
            
            return np.array(sma_values)
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return values.copy()
    
    def _calculate_ema(self, values: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        try:
            if len(values) < period:
                return values.copy()
            
            multiplier = 2.0 / (period + 1.0)
            ema_values = [values[0]]
            
            for i in range(1, len(values)):
                ema = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
                ema_values.append(ema)
            
            return np.array(ema_values)
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return values.copy()
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14) -> Dict[str, np.ndarray]:
        """Calculate Stochastic Oscillator"""
        try:
            prices = df['price'].values
            k_values = []
            
            for i in range(len(prices)):
                if i < k_period - 1:
                    k_values.append(50.0)
                else:
                    window = prices[i - k_period + 1:i + 1]
                    highest = np.max(window)
                    lowest = np.min(window)
                    
                    if highest == lowest:
                        k = 50.0
                    else:
                        k = ((prices[i] - lowest) / (highest - lowest)) * 100.0
                    
                    k_values.append(k)
            
            k_array = np.array(k_values)
            d_array = self._calculate_sma(k_array, 3)
            
            return {'k': k_array, 'd': d_array}
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return {'k': np.array([50.0] * len(df)), 'd': np.array([50.0] * len(df))}
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Williams %R"""
        try:
            prices = df['price'].values
            wr_values = []
            
            for i in range(len(prices)):
                if i < period - 1:
                    wr_values.append(-50.0)
                else:
                    window = prices[i - period + 1:i + 1]
                    highest = np.max(window)
                    lowest = np.min(window)
                    
                    if highest == lowest:
                        wr = -50.0
                    else:
                        wr = ((highest - prices[i]) / (highest - lowest)) * -100.0
                    
                    wr_values.append(wr)
            
            return np.array(wr_values)
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return np.array([-50.0] * len(df))
    
    def _calculate_volume_ratio(self, volumes: np.ndarray) -> float:
        """Calculate volume ratio"""
        try:
            if len(volumes) < 20:
                return 1.0
            
            current_volume = volumes[-1]
            avg_volume = np.mean(volumes[-20:])
            
            if avg_volume == 0:
                return 1.0
            
            return current_volume / avg_volume
            
        except Exception as e:
            logger.error(f"Error calculating volume ratio: {e}")
            return 1.0
    
    def _detect_patterns(self, prices: np.ndarray, indicators: Dict) -> List[str]:
        """Detect chart patterns"""
        patterns = []
        
        try:
            # Golden Cross
            sma_20 = indicators["sma_20"]
            sma_50 = indicators["sma_50"]
            if len(sma_20) > 1 and len(sma_50) > 1:
                if sma_20[-1] > sma_50[-1] and sma_20[-2] <= sma_50[-2]:
                    patterns.append("Golden Cross")
                elif sma_20[-1] < sma_50[-1] and sma_20[-2] >= sma_50[-2]:
                    patterns.append("Death Cross")
            
            # MACD Signal
            macd = indicators["macd"]
            if len(macd["macd"]) > 1 and len(macd["signal"]) > 1:
                if macd["macd"][-1] > macd["signal"][-1] and macd["macd"][-2] <= macd["signal"][-2]:
                    patterns.append("MACD Bullish Cross")
                elif macd["macd"][-1] < macd["signal"][-1] and macd["macd"][-2] >= macd["signal"][-2]:
                    patterns.append("MACD Bearish Cross")
            
            # Bollinger Squeeze
            bollinger = indicators["bollinger"]
            if len(bollinger["upper"]) > 0:
                bandwidth = (bollinger["upper"][-1] - bollinger["lower"][-1]) / bollinger["middle"][-1]
                if bandwidth < 0.1:  # Tight bands
                    patterns.append("Bollinger Squeeze")
            
            # Support/Resistance Break
            current_price = prices[-1]
            support_levels = self._find_support_levels(prices)
            resistance_levels = self._find_resistance_levels(prices)
            
            for level in resistance_levels:
                if current_price > level * 1.02:  # 2% above resistance
                    patterns.append("Resistance Break")
                    break
            
            for level in support_levels:
                if current_price < level * 0.98:  # 2% below support
                    patterns.append("Support Break")
                    break
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
        
        return patterns
    
    def _generate_signals(self, indicators: Dict, patterns: List[str]) -> List[str]:
        """Generate trading signals"""
        signals = []
        
        try:
            # RSI signals
            rsi = indicators["rsi"][-1]
            if rsi < 30:
                signals.append("RSI Oversold")
            elif rsi > 70:
                signals.append("RSI Overbought")
            
            # Volume signals
            volume_ratio = indicators["volume_ratio"]
            if volume_ratio > 2.0:
                signals.append("High Volume")
            elif volume_ratio < 0.5:
                signals.append("Low Volume")
            
            # Pattern-based signals
            bullish_patterns = ["Golden Cross", "MACD Bullish Cross", "Resistance Break", "Bollinger Squeeze"]
            bearish_patterns = ["Death Cross", "MACD Bearish Cross", "Support Break"]
            
            for pattern in patterns:
                if pattern in bullish_patterns:
                    signals.append(f"Bullish {pattern}")
                elif pattern in bearish_patterns:
                    signals.append(f"Bearish {pattern}")
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
        
        return signals
    
    def _calculate_technical_score(self, indicators: Dict, signals: List[str]) -> int:
        """Calculate technical score 0-100"""
        try:
            score = 50  # Neutral base
            
            # RSI contribution
            rsi = indicators["rsi"][-1]
            if 30 <= rsi <= 70:
                score += 10  # Neutral RSI is good
            elif rsi < 30:
                score += 15  # Oversold can be bullish
            elif rsi > 70:
                score -= 15  # Overbought can be bearish
            
            # MACD contribution
            macd = indicators["macd"]
            if macd["macd"][-1] > macd["signal"][-1]:
                score += 10
            else:
                score -= 10
            
            # Moving Average contribution
            sma_20 = indicators["sma_20"][-1]
            sma_50 = indicators["sma_50"][-1]
            if sma_20 > sma_50:
                score += 10
            else:
                score -= 10
            
            # Volume contribution
            volume_ratio = indicators["volume_ratio"]
            if volume_ratio > 1.5:
                score += 5
            elif volume_ratio < 0.7:
                score -= 5
            
            # Signals contribution
            bullish_signals = [s for s in signals if "Bullish" in s or "Oversold" in s or "High Volume" in s]
            bearish_signals = [s for s in signals if "Bearish" in s or "Overbought" in s or "Low Volume" in s]
            
            score += len(bullish_signals) * 5
            score -= len(bearish_signals) * 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return 50
    
    def _get_recommendation(self, score: int, signals: List[str]) -> str:
        """Get recommendation based on score and signals"""
        try:
            if score >= 70:
                return "BUY"
            elif score <= 30:
                return "SELL"
            else:
                return "HOLD"
        except:
            return "HOLD"
    
    def _calculate_confidence(self, indicators: Dict, signals: List[str]) -> float:
        """Calculate confidence level"""
        try:
            confidence = 0.5  # Base confidence
            
            # More signals = higher confidence
            if len(signals) >= 3:
                confidence += 0.2
            elif len(signals) >= 2:
                confidence += 0.1
            
            # Volume confirmation
            volume_ratio = indicators["volume_ratio"]
            if volume_ratio > 1.5:
                confidence += 0.1
            
            # RSI in normal range
            rsi = indicators["rsi"][-1]
            if 20 <= rsi <= 80:
                confidence += 0.1
            
            return min(0.95, max(0.3, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_bollinger_position(self, price: float, bollinger: Dict) -> str:
        """Get Bollinger Band position"""
        try:
            upper = bollinger["upper"][-1]
            middle = bollinger["middle"][-1]
            lower = bollinger["lower"][-1]
            
            if price > upper:
                return "above_upper"
            elif price > middle:
                return "upper_half"
            elif price > lower:
                return "lower_half"
            else:
                return "below_lower"
        except:
            return "middle"
    
    def _find_support_levels(self, prices: np.ndarray) -> List[float]:
        """Find support levels"""
        try:
            if len(prices) < 20:
                return [float(np.min(prices))]
            
            # Find local minima
            peaks, _ = find_peaks(-prices, distance=10)
            support_levels = [float(prices[peak]) for peak in peaks[-3:]]  # Last 3 supports
            
            if not support_levels:
                support_levels = [float(np.min(prices[-50:]))]  # Recent low
            
            return sorted(support_levels)
            
        except Exception as e:
            logger.error(f"Error finding support levels: {e}")
            return [float(np.min(prices)) if len(prices) > 0 else 0.0]
    
    def _find_resistance_levels(self, prices: np.ndarray) -> List[float]:
        """Find resistance levels"""
        try:
            if len(prices) < 20:
                return [float(np.max(prices))]
            
            # Find local maxima
            peaks, _ = find_peaks(prices, distance=10)
            resistance_levels = [float(prices[peak]) for peak in peaks[-3:]]  # Last 3 resistances
            
            if not resistance_levels:
                resistance_levels = [float(np.max(prices[-50:]))]  # Recent high
            
            return sorted(resistance_levels, reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding resistance levels: {e}")
            return [float(np.max(prices)) if len(prices) > 0 else 0.0]
    
    def _generate_overall_recommendation(self, timeframe_analysis: Dict) -> Dict[str, Any]:
        """Generate overall recommendation from all timeframes"""
        try:
            if not timeframe_analysis:
                return {
                    "recommendation": "HOLD",
                    "score": 50,
                    "confidence": 0.3,
                    "signals": ["Insufficient data"],
                    "risk_level": "Medium"
                }
            
            # Weight timeframes (longer timeframes have more weight)
            weights = {"30m": 0.1, "1h": 0.2, "4h": 0.3, "1d": 0.4}
            
            total_score = 0
            total_weight = 0
            all_signals = []
            
            for tf, analysis in timeframe_analysis.items():
                if "score" in analysis:
                    weight = weights.get(tf, 0.25)
                    total_score += analysis["score"] * weight
                    total_weight += weight
                    
                    if "signals" in analysis:
                        all_signals.extend(analysis["signals"])
            
            if total_weight == 0:
                overall_score = 50
            else:
                overall_score = int(total_score / total_weight)
            
            # Overall recommendation
            if overall_score >= 70:
                recommendation = "BUY"
                risk_level = "Medium"
            elif overall_score <= 30:
                recommendation = "SELL"
                risk_level = "High"
            else:
                recommendation = "HOLD"
                risk_level = "Low"
            
            # Calculate overall confidence
            confidences = [analysis.get("confidence", 0.5) for analysis in timeframe_analysis.values()]
            overall_confidence = np.mean(confidences) if confidences else 0.5
            
            # Get unique signals
            unique_signals = list(set(all_signals))[:5]  # Top 5 signals
            
            return {
                "recommendation": recommendation,
                "score": overall_score,
                "confidence": overall_confidence,
                "signals": unique_signals,
                "risk_level": risk_level
            }
            
        except Exception as e:
            logger.error(f"Error generating overall recommendation: {e}")
            return {
                "recommendation": "HOLD",
                "score": 50,
                "confidence": 0.3,
                "signals": ["Analysis error"],
                "risk_level": "Medium"
            }
    
    def _generate_fallback_analysis(self, symbol: str) -> Dict[str, Any]:
        """Generate fallback analysis when data is unavailable"""
        return {
            "symbol": symbol.upper(),
            "timeframe_analysis": {},
            "overall_recommendation": "HOLD",
            "overall_score": 50,
            "overall_confidence": 0.3,
            "key_signals": ["Data unavailable"],
            "risk_level": "Unknown",
            "timestamp": datetime.now().isoformat(),
            "error": "Unable to fetch market data"
        }


# Global instance
technical_analysis_service = RealTechnicalAnalysisService()

