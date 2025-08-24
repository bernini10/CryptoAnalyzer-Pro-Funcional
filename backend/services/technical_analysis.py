"""
Technical Analysis Service - REAL IMPLEMENTATION
Provides comprehensive cryptocurrency technical analysis with real data
"""

import asyncio
import aiohttp
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
"""
Technical Analysis Service - REAL IMPLEMENTATION
Provides comprehensive cryptocurrency technical analysis with real data
"""

import asyncio
import aiohttp
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
from .coingecko_service import coingecko_service

logger = logging.getLogger(__name__)


class RealTechnicalAnalysisService:
    """Real technical analysis service with multiple timeframes and comprehensive indicators"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = int(os.getenv('CACHE_TTL_TECHNICAL_ANALYSIS', 600))  # 10 minutes
        
        # Technical Analysis Parameters from .env
        self.rsi_period = int(os.getenv('RSI_PERIOD', 14))
        self.rsi_oversold = int(os.getenv('RSI_OVERSOLD', 30))
        self.rsi_overbought = int(os.getenv('RSI_OVERBOUGHT', 70))
        
        self.macd_fast = int(os.getenv('MACD_FAST', 12))
        self.macd_slow = int(os.getenv('MACD_SLOW', 26))
        self.macd_signal = int(os.getenv('MACD_SIGNAL', 9))
        
        self.bollinger_period = int(os.getenv('BOLLINGER_PERIOD', 20))
        self.bollinger_std = float(os.getenv('BOLLINGER_STD', 2))
        
        # Multiple timeframes as requested
        self.timeframes = ['30m', '1h', '4h', '1d', '1w']
        self.timeframe_days = {
            '30m': 7,    # 7 days for 30min data
            '1h': 14,    # 14 days for 1h data  
            '4h': 30,    # 30 days for 4h data
            '1d': 365,   # 1 year for daily data
            '1w': 730    # 2 years for weekly data
        }
    
    async def comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform comprehensive analysis across all timeframes"""
        try:
            cache_key = f"comprehensive_{symbol}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get coin ID from symbol
            coin_id = await self._get_coin_id(symbol)
            if not coin_id:
                raise ValueError(f"Could not find coin ID for symbol {symbol}")
            
            # Analyze all timeframes
            analysis_results = {}
            
            for timeframe in self.timeframes:
                try:
                    timeframe_analysis = await self._analyze_timeframe(coin_id, timeframe)
                    analysis_results[timeframe] = timeframe_analysis
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} on {timeframe}: {e}")
                    analysis_results[timeframe] = self._get_error_analysis()
            
            # Generate overall recommendation
            overall_recommendation = self._generate_overall_recommendation(analysis_results)
            
            # Calculate comprehensive score
            comprehensive_score = self._calculate_comprehensive_score(analysis_results)
            
            # Generate trading signals
            trading_signals = self._generate_trading_signals(analysis_results)
            
            # Risk assessment
            risk_assessment = self._assess_risk(analysis_results)
            
            comprehensive_analysis = {
                "symbol": symbol.upper(),
                "coin_id": coin_id,
                "timestamp": datetime.now().isoformat(),
                "timeframe_analysis": analysis_results,
                "overall_recommendation": overall_recommendation,
                "comprehensive_score": comprehensive_score,
                "trading_signals": trading_signals,
                "risk_assessment": risk_assessment,
                "market_structure": await self._analyze_market_structure(analysis_results),
                "volume_analysis": self._analyze_volume_patterns(analysis_results),
                "momentum_analysis": self._analyze_momentum(analysis_results),
                "trend_analysis": self._analyze_trends(analysis_results)
            }
            
            # Cache result
            self.cache[cache_key] = {
                "data": comprehensive_analysis,
                "timestamp": datetime.now()
            }
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            raise
    
    async def _analyze_timeframe(self, coin_id: str, timeframe: str) -> Dict[str, Any]:
        """Analyze single timeframe with all indicators"""
        try:
            # Get historical data
            days = self.timeframe_days[timeframe]
            interval = self._get_coingecko_interval(timeframe)
            
            historical_data = await coingecko_service.get_historical_data(
                coin_id=coin_id,
                days=days,
                interval=interval
            )
            
            if not historical_data or len(historical_data) < 50:
                return self._get_insufficient_data_analysis()
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(historical_data)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            df.sort_index(inplace=True)
            
            # Calculate all technical indicators
            indicators = await self._calculate_all_indicators(df)
            
            # Generate signals for this timeframe
            signals = self._generate_timeframe_signals(indicators, df)
            
            # Support and resistance levels
            support_resistance = self._calculate_support_resistance(df)
            
            # Pattern recognition
            patterns = self._detect_patterns(df)
            
            # Fibonacci levels
            fibonacci = self._calculate_fibonacci_levels(df)
            
            return {
                "timeframe": timeframe,
                "data_points": len(df),
                "current_price": float(df['price'].iloc[-1]),
                "price_change_24h": self._calculate_price_change(df, 24),
                "indicators": indicators,
                "signals": signals,
                "support_resistance": support_resistance,
                "patterns": patterns,
                "fibonacci": fibonacci,
                "volume_profile": self._analyze_volume_profile(df),
                "market_microstructure": self._analyze_microstructure(df)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timeframe {timeframe} for {coin_id}: {e}")
            return self._get_error_analysis()
    
    async def _calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        try:
            prices = df['price'].values
            volumes = df['volume'].values
            
            indicators = {}
            
            # RSI with multiple periods
            indicators['rsi'] = {
                'rsi_14': self._calculate_rsi(prices, 14),
                'rsi_21': self._calculate_rsi(prices, 21),
                'rsi_30': self._calculate_rsi(prices, 30),
                'current_rsi': self._calculate_rsi(prices, 14)[-1] if len(prices) >= 14 else 50.0,
                'oversold_level': self.rsi_oversold,
                'overbought_level': self.rsi_overbought
            }
            
            # MACD with multiple configurations
            macd_data = self._calculate_macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
            
            indicators['macd'] = {
                'macd_line': macd_data['macd'],
                'signal_line': macd_data['signal'],
                'histogram': macd_data['histogram'],
                'current_macd': macd_data['macd'][-1] if macd_data['macd'] else 0.0,
                'current_signal': macd_data['signal'][-1] if macd_data['signal'] else 0.0,
                'current_histogram': macd_data['histogram'][-1] if macd_data['histogram'] else 0.0
            }
            
            # Bollinger Bands
            bb_data = self._calculate_bollinger_bands(prices, self.bollinger_period, self.bollinger_std)
            
            indicators['bollinger_bands'] = {
                'upper': bb_data['upper'],
                'middle': bb_data['middle'],
                'lower': bb_data['lower'],
                'current_upper': bb_data['upper'][-1] if bb_data['upper'] else 0.0,
                'current_middle': bb_data['middle'][-1] if bb_data['middle'] else 0.0,
                'current_lower': bb_data['lower'][-1] if bb_data['lower'] else 0.0,
                'squeeze': self._detect_bollinger_squeeze(bb_data)
            }
            
            # Moving Averages (comprehensive set)
            indicators['moving_averages'] = {
                'sma_10': self._calculate_sma(prices, 10),
                'sma_20': self._calculate_sma(prices, 20),
                'sma_50': self._calculate_sma(prices, 50),
                'sma_100': self._calculate_sma(prices, 100),
                'sma_200': self._calculate_sma(prices, 200),
                'ema_10': self._calculate_ema(prices, 10),
                'ema_20': self._calculate_ema(prices, 20),
                'ema_50': self._calculate_ema(prices, 50),
                'ema_100': self._calculate_ema(prices, 100),
                'ema_200': self._calculate_ema(prices, 200)
            }
            
            # Momentum Indicators
            indicators['momentum'] = {
                'stoch': self._calculate_stochastic(df),
                'williams_r': self._calculate_williams_r(df),
                'roc': self._calculate_roc(prices, 10),
                'momentum': self._calculate_momentum(prices, 10)
            }
            
            # Volume Indicators
            if len(volumes) > 0:
                indicators['volume'] = {
                    'volume_sma_20': self._calculate_sma(volumes, 20),
                    'volume_ema_20': self._calculate_ema(volumes, 20),
                    'obv': self._calculate_obv(prices, volumes),
                    'ad_line': self._calculate_ad_line(df),
                    'volume_ratio': self._calculate_volume_ratio(volumes)
                }
            
            # Volatility Indicators
            indicators['volatility'] = {
                'atr': self._calculate_atr(df, 14),
                'true_range': self._calculate_true_range(df),
                'volatility_ratio': self._calculate_volatility_ratio(prices)
            }
            
            # Trend Indicators
            indicators['trend'] = {
                'adx': self._calculate_adx(df, 14),
                'cci': self._calculate_cci(df, 14),
                'aroon': self._calculate_aroon(df, 14),
                'parabolic_sar': self._calculate_parabolic_sar(df)
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> List[float]:
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return [50.0] * len(prices)
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            rsi_values = []
            
            # Calculate initial average gain and loss
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            for i in range(period, len(prices)):
                if i == period:
                    # First RSI calculation
                    if avg_loss == 0:
                        rsi = 100
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                else:
                    # Smoothed RSI calculation
                    current_gain = gains[i-1] if i-1 < len(gains) else 0
                    current_loss = losses[i-1] if i-1 < len(losses) else 0
                    
                    avg_gain = ((avg_gain * (period - 1)) + current_gain) / period
                    avg_loss = ((avg_loss * (period - 1)) + current_loss) / period
                    
                    if avg_loss == 0:
                        rsi = 100
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append(rsi)
            
            # Pad with initial values
            result = [50.0] * period + rsi_values
            return result[:len(prices)]
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return [50.0] * len(prices)
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """Calculate MACD indicator"""
        try:
            if len(prices) < slow:
                return {'macd': [0.0] * len(prices), 'signal': [0.0] * len(prices), 'histogram': [0.0] * len(prices)}
            
            # Calculate EMAs
            ema_fast = self._calculate_ema(prices, fast)
            ema_slow = self._calculate_ema(prices, slow)
            
            # Calculate MACD line
            macd_line = [fast_val - slow_val for fast_val, slow_val in zip(ema_fast, ema_slow)]
            
            # Calculate signal line (EMA of MACD)
            signal_line = self._calculate_ema(np.array(macd_line), signal)
            
            # Calculate histogram
            histogram = [macd_val - signal_val for macd_val, signal_val in zip(macd_line, signal_line)]
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {'macd': [0.0] * len(prices), 'signal': [0.0] * len(prices), 'histogram': [0.0] * len(prices)}
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                current_price = prices[-1] if len(prices) > 0 else 100.0
                return {
                    'upper': [current_price * 1.02] * len(prices),
                    'middle': [current_price] * len(prices),
                    'lower': [current_price * 0.98] * len(prices)
                }
            
            sma = self._calculate_sma(prices, period)
            upper = []
            lower = []
            
            for i in range(len(prices)):
                if i < period - 1:
                    upper.append(sma[i] * 1.02)
                    lower.append(sma[i] * 0.98)
                else:
                    # Calculate standard deviation for the period
                    period_prices = prices[i-period+1:i+1]
                    std = np.std(period_prices)
                    
                    upper.append(sma[i] + (std_dev * std))
                    lower.append(sma[i] - (std_dev * std))
            
            return {
                'upper': upper,
                'middle': sma,
                'lower': lower
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {'upper': [], 'middle': [], 'lower': []}
    
    def _calculate_sma(self, prices: np.ndarray, period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) < period:
                return [np.mean(prices)] * len(prices)
            
            sma = []
            for i in range(len(prices)):
                if i < period - 1:
                    sma.append(np.mean(prices[:i+1]))
                else:
                    sma.append(np.mean(prices[i-period+1:i+1]))
            
            return sma
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return [0.0] * len(prices)
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) == 0:
                return []
            
            multiplier = 2 / (period + 1)
            ema = [prices[0]]  # First EMA is the first price
            
            for i in range(1, len(prices)):
                ema_value = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
                ema.append(ema_value)
            
            return ema
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return [0.0] * len(prices)
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, List[float]]:
        """Calculate Stochastic Oscillator"""
        try:
            prices = df['price'].values
            if len(prices) < k_period:
                return {'%K': [50.0] * len(prices), '%D': [50.0] * len(prices)}
            
            k_values = []
            
            for i in range(len(prices)):
                if i < k_period - 1:
                    k_values.append(50.0)
                else:
                    period_prices = prices[i-k_period+1:i+1]
                    lowest_low = np.min(period_prices)
                    highest_high = np.max(period_prices)
                    
                    if highest_high - lowest_low == 0:
                        k_value = 50.0
                    else:
                        k_value = ((prices[i] - lowest_low) / (highest_high - lowest_low)) * 100
                    
                    k_values.append(k_value)
            
            # Calculate %D (SMA of %K)
            d_values = self._calculate_sma(np.array(k_values), d_period)
            
            return {'%K': k_values, '%D': d_values}
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return {'%K': [50.0] * len(df), '%D': [50.0] * len(df)}
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> List[float]:
        """Calculate Williams %R"""
        try:
            prices = df['price'].values
            if len(prices) < period:
                return [-50.0] * len(prices)
            
            williams_r = []
            
            for i in range(len(prices)):
                if i < period - 1:
                    williams_r.append(-50.0)
                else:
                    period_prices = prices[i-period+1:i+1]
                    highest_high = np.max(period_prices)
                    lowest_low = np.min(period_prices)
                    
                    if highest_high - lowest_low == 0:
                        wr_value = -50.0
                    else:
                        wr_value = ((highest_high - prices[i]) / (highest_high - lowest_low)) * -100
                    
                    williams_r.append(wr_value)
            
            return williams_r
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return [-50.0] * len(df)
    
    def _calculate_roc(self, prices: np.ndarray, period: int = 10) -> List[float]:
        """Calculate Rate of Change"""
        try:
            if len(prices) < period + 1:
                return [0.0] * len(prices)
            
            roc = []
            
            for i in range(len(prices)):
                if i < period:
                    roc.append(0.0)
                else:
                    if prices[i-period] != 0:
                        roc_value = ((prices[i] - prices[i-period]) / prices[i-period]) * 100
                    else:
                        roc_value = 0.0
                    roc.append(roc_value)
            
            return roc
            
        except Exception as e:
            logger.error(f"Error calculating ROC: {e}")
            return [0.0] * len(prices)
    
    def _calculate_momentum(self, prices: np.ndarray, period: int = 10) -> List[float]:
        """Calculate Momentum"""
        try:
            if len(prices) < period + 1:
                return [0.0] * len(prices)
            
            momentum = []
            
            for i in range(len(prices)):
                if i < period:
                    momentum.append(0.0)
                else:
                    mom_value = prices[i] - prices[i-period]
                    momentum.append(mom_value)
            
            return momentum
            
        except Exception as e:
            logger.error(f"Error calculating Momentum: {e}")
            return [0.0] * len(prices)
    
    def _calculate_obv(self, prices: np.ndarray, volumes: np.ndarray) -> List[float]:
        """Calculate On-Balance Volume"""
        try:
            if len(prices) != len(volumes) or len(prices) < 2:
                return [0.0] * len(prices)
            
            obv = [volumes[0]]
            
            for i in range(1, len(prices)):
                if prices[i] > prices[i-1]:
                    obv.append(obv[-1] + volumes[i])
                elif prices[i] < prices[i-1]:
                    obv.append(obv[-1] - volumes[i])
                else:
                    obv.append(obv[-1])
            
            return obv
            
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return [0.0] * len(prices)
    
    def _calculate_ad_line(self, df: pd.DataFrame) -> List[float]:
        """Calculate Accumulation/Distribution Line"""
        try:
            prices = df['price'].values
            volumes = df['volume'].values
            
            if len(prices) < 1:
                return [0.0]
            
            ad_line = [0.0]
            
            for i in range(1, len(prices)):
                # Simplified A/D calculation (assuming high=low=close for simplicity)
                high = low = close = prices[i]
                volume = volumes[i] if i < len(volumes) else 0
                
                if high - low != 0:
                    money_flow_multiplier = ((close - low) - (high - close)) / (high - low)
                else:
                    money_flow_multiplier = 0
                
                money_flow_volume = money_flow_multiplier * volume
                ad_line.append(ad_line[-1] + money_flow_volume)
            
            return ad_line
            
        except Exception as e:
            logger.error(f"Error calculating A/D Line: {e}")
            return [0.0] * len(df)
    
    def _calculate_volume_ratio(self, volumes: np.ndarray) -> float:
        """Calculate current volume ratio to average"""
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
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> List[float]:
        """Calculate Average True Range"""
        try:
            prices = df['price'].values
            if len(prices) < 2:
                return [0.0] * len(prices)
            
            true_ranges = self._calculate_true_range(df)
            atr = self._calculate_sma(np.array(true_ranges), period)
            
            return atr
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return [0.0] * len(df)
    
    def _calculate_true_range(self, df: pd.DataFrame) -> List[float]:
        """Calculate True Range"""
        try:
            prices = df['price'].values
            if len(prices) < 2:
                return [0.0] * len(prices)
            
            true_ranges = [0.0]  # First value is 0
            
            for i in range(1, len(prices)):
                # Simplified TR calculation (assuming high=low=close)
                high = low = close = prices[i]
                prev_close = prices[i-1]
                
                tr1 = high - low
                tr2 = abs(high - prev_close)
                tr3 = abs(low - prev_close)
                
                true_range = max(tr1, tr2, tr3)
                true_ranges.append(true_range)
            
            return true_ranges
            
        except Exception as e:
            logger.error(f"Error calculating True Range: {e}")
            return [0.0] * len(df)
    
    def _calculate_volatility_ratio(self, prices: np.ndarray) -> float:
        """Calculate volatility ratio"""
        try:
            if len(prices) < 20:
                return 1.0
            
            recent_volatility = np.std(prices[-10:])
            historical_volatility = np.std(prices[-20:])
            
            if historical_volatility == 0:
                return 1.0
            
            return recent_volatility / historical_volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility ratio: {e}")
            return 1.0
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> List[float]:
        """Calculate Average Directional Index"""
        try:
            prices = df['price'].values
            if len(prices) < period * 2:
                return [25.0] * len(prices)
            
            # Simplified ADX calculation
            # In a real implementation, this would be more complex
            price_changes = np.diff(prices)
            positive_changes = np.where(price_changes > 0, price_changes, 0)
            negative_changes = np.where(price_changes < 0, -price_changes, 0)
            
            adx_values = []
            for i in range(len(prices)):
                if i < period:
                    adx_values.append(25.0)
                else:
                    # Simplified ADX calculation
                    recent_pos = np.mean(positive_changes[max(0, i-period):i])
                    recent_neg = np.mean(negative_changes[max(0, i-period):i])
                    
                    if recent_pos + recent_neg == 0:
                        adx = 25.0
                    else:
                        dx = abs(recent_pos - recent_neg) / (recent_pos + recent_neg) * 100
                        adx = min(100, max(0, dx))
                    
                    adx_values.append(adx)
            
            return adx_values
            
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return [25.0] * len(df)
    
    def _calculate_cci(self, df: pd.DataFrame, period: int = 14) -> List[float]:
        """Calculate Commodity Channel Index"""
        try:
            prices = df['price'].values
            if len(prices) < period:
                return [0.0] * len(prices)
            
            typical_prices = prices  # Simplified: using close price as typical price
            sma_tp = self._calculate_sma(typical_prices, period)
            
            cci_values = []
            
            for i in range(len(prices)):
                if i < period - 1:
                    cci_values.append(0.0)
                else:
                    # Calculate mean deviation
                    period_tp = typical_prices[i-period+1:i+1]
                    mean_deviation = np.mean(np.abs(period_tp - sma_tp[i]))
                    
                    if mean_deviation == 0:
                        cci = 0.0
                    else:
                        cci = (typical_prices[i] - sma_tp[i]) / (0.015 * mean_deviation)
                    
                    cci_values.append(cci)
            
            return cci_values
            
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return [0.0] * len(df)
    
    def _calculate_aroon(self, df: pd.DataFrame, period: int = 14) -> Dict[str, List[float]]:
        """Calculate Aroon Up and Aroon Down"""
        try:
            prices = df['price'].values
            if len(prices) < period:
                return {'aroon_up': [50.0] * len(prices), 'aroon_down': [50.0] * len(prices)}
            
            aroon_up = []
            aroon_down = []
            
            for i in range(len(prices)):
                if i < period - 1:
                    aroon_up.append(50.0)
                    aroon_down.append(50.0)
                else:
                    period_prices = prices[i-period+1:i+1]
                    
                    # Find periods since highest high and lowest low
                    highest_idx = np.argmax(period_prices)
                    lowest_idx = np.argmin(period_prices)
                    
                    periods_since_high = period - 1 - highest_idx
                    periods_since_low = period - 1 - lowest_idx
                    
                    aroon_up_val = ((period - periods_since_high) / period) * 100
                    aroon_down_val = ((period - periods_since_low) / period) * 100
                    
                    aroon_up.append(aroon_up_val)
                    aroon_down.append(aroon_down_val)
            
            return {'aroon_up': aroon_up, 'aroon_down': aroon_down}
            
        except Exception as e:
            logger.error(f"Error calculating Aroon: {e}")
            return {'aroon_up': [50.0] * len(df), 'aroon_down': [50.0] * len(df)}
    
    def _calculate_parabolic_sar(self, df: pd.DataFrame, af_start: float = 0.02, af_max: float = 0.2) -> List[float]:
        """Calculate Parabolic SAR"""
        try:
            prices = df['price'].values
            if len(prices) < 2:
                return prices.tolist()
            
            sar = [prices[0]]
            af = af_start
            ep = prices[0]  # Extreme point
            trend = 1  # 1 for uptrend, -1 for downtrend
            
            for i in range(1, len(prices)):
                # Calculate SAR
                sar_value = sar[-1] + af * (ep - sar[-1])
                
                # Check for trend reversal
                if trend == 1:  # Uptrend
                    if prices[i] < sar_value:
                        # Trend reversal to downtrend
                        trend = -1
                        sar_value = ep
                        ep = prices[i]
                        af = af_start
                    else:
                        if prices[i] > ep:
                            ep = prices[i]
                            af = min(af + af_start, af_max)
                else:  # Downtrend
                    if prices[i] > sar_value:
                        # Trend reversal to uptrend
                        trend = 1
                        sar_value = ep
                        ep = prices[i]
                        af = af_start
                    else:
                        if prices[i] < ep:
                            ep = prices[i]
                            af = min(af + af_start, af_max)
                
                sar.append(sar_value)
            
            return sar
            
        except Exception as e:
            logger.error(f"Error calculating Parabolic SAR: {e}")
            return prices.tolist()
    
    def _detect_bollinger_squeeze(self, bb_data: Dict[str, List[float]]) -> bool:
        """Detect Bollinger Band squeeze"""
        try:
            if not bb_data or not bb_data.get('upper') or not bb_data.get('lower') or not bb_data.get('middle'):
                return False
            
            upper = bb_data['upper']
            lower = bb_data['lower']
            middle = bb_data['middle']
            
            if len(upper) < 20:
                return False
            
            # Calculate band width for recent periods
            recent_widths = []
            for i in range(-20, 0):
                if abs(i) <= len(upper):
                    width = (upper[i] - lower[i]) / middle[i] if middle[i] != 0 else 0
                    recent_widths.append(width)
            
            if not recent_widths:
                return False
            
            current_width = recent_widths[-1]
            avg_width = np.mean(recent_widths[:-1])
            
            # Squeeze detected if current width is significantly smaller than average
            return current_width < avg_width * 0.8
            
        except Exception as e:
            logger.error(f"Error detecting Bollinger squeeze: {e}")
            return False
    
    async def comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform comprehensive analysis across all timeframes"""
        try:
            cache_key = f"comprehensive_{symbol}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get coin ID from symbol
            coin_id = await self._get_coin_id(symbol)
            if not coin_id:
                raise ValueError(f"Could not find coin ID for symbol {symbol}")
            
            # Analyze all timeframes
            analysis_results = {}
            
            for timeframe in self.timeframes:
                try:
                    timeframe_analysis = await self._analyze_timeframe(coin_id, timeframe)
                    analysis_results[timeframe] = timeframe_analysis
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} on {timeframe}: {e}")
                    analysis_results[timeframe] = self._get_error_analysis()
            
            # Generate overall recommendation
            overall_recommendation = self._generate_overall_recommendation(analysis_results)
            
            # Calculate comprehensive score
            comprehensive_score = self._calculate_comprehensive_score(analysis_results)
            
            # Generate trading signals
            trading_signals = self._generate_trading_signals(analysis_results)
            
            # Risk assessment
            risk_assessment = self._assess_risk(analysis_results)
            
            comprehensive_analysis = {
                "symbol": symbol.upper(),
                "coin_id": coin_id,
                "timestamp": datetime.now().isoformat(),
                "timeframe_analysis": analysis_results,
                "overall_recommendation": overall_recommendation,
                "comprehensive_score": comprehensive_score,
                "trading_signals": trading_signals,
                "risk_assessment": risk_assessment,
                "market_structure": await self._analyze_market_structure(analysis_results),
                "volume_analysis": self._analyze_volume_patterns(analysis_results),
                "momentum_analysis": self._analyze_momentum(analysis_results),
                "trend_analysis": self._analyze_trends(analysis_results)
            }
            
            # Cache result
            self.cache[cache_key] = {
                "data": comprehensive_analysis,
                "timestamp": datetime.now()
            }
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            raise
    
    async def _analyze_timeframe(self, coin_id: str, timeframe: str) -> Dict[str, Any]:
        """Analyze single timeframe with all indicators"""
        try:
            # Get historical data
            days = self.timeframe_days[timeframe]
            interval = self._get_coingecko_interval(timeframe)
            
            historical_data = await coingecko_service.get_historical_data(
                coin_id=coin_id,
                days=days,
                interval=interval
            )
            
            if not historical_data or len(historical_data) < 50:
                return self._get_insufficient_data_analysis()
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(historical_data)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            df.sort_index(inplace=True)
            
            # Calculate all technical indicators
            indicators = await self._calculate_all_indicators(df)
            
            # Generate signals for this timeframe
            signals = self._generate_timeframe_signals(indicators, df)
            
            # Support and resistance levels
            support_resistance = self._calculate_support_resistance(df)
            
            # Pattern recognition
            patterns = self._detect_patterns(df)
            
            # Fibonacci levels
            fibonacci = self._calculate_fibonacci_levels(df)
            
            return {
                "timeframe": timeframe,
                "data_points": len(df),
                "current_price": float(df['price'].iloc[-1]),
                "price_change_24h": self._calculate_price_change(df, 24),
                "indicators": indicators,
                "signals": signals,
                "support_resistance": support_resistance,
                "patterns": patterns,
                "fibonacci": fibonacci,
                "volume_profile": self._analyze_volume_profile(df),
                "market_microstructure": self._analyze_microstructure(df)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timeframe {timeframe} for {coin_id}: {e}")
            return self._get_error_analysis()
    
    async def _calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        try:
            prices = df['price'].values
            volumes = df['volume'].values
            
            indicators = {}
            
            # RSI with multiple periods
            indicators['rsi'] = {
                'rsi_14': self._safe_talib_call(talib.RSI, prices, timeperiod=14),
                'rsi_21': self._safe_talib_call(talib.RSI, prices, timeperiod=21),
                'rsi_30': self._safe_talib_call(talib.RSI, prices, timeperiod=30),
                'current_rsi': float(talib.RSI(prices, timeperiod=14)[-1]) if len(prices) >= 14 else 50.0,
                'oversold_level': self.rsi_oversold,
                'overbought_level': self.rsi_overbought
            }
            
            # MACD with multiple configurations
            macd, macd_signal, macd_hist = talib.MACD(prices, 
                                                     fastperiod=self.macd_fast,
                                                     slowperiod=self.macd_slow, 
                                                     signalperiod=self.macd_signal)
            
            indicators['macd'] = {
                'macd_line': self._safe_array_to_list(macd),
                'signal_line': self._safe_array_to_list(macd_signal),
                'histogram': self._safe_array_to_list(macd_hist),
                'current_macd': float(macd[-1]) if not np.isnan(macd[-1]) else 0.0,
                'current_signal': float(macd_signal[-1]) if not np.isnan(macd_signal[-1]) else 0.0,
                'current_histogram': float(macd_hist[-1]) if not np.isnan(macd_hist[-1]) else 0.0
            }
            
            # Bollinger Bands with multiple periods
            bb_upper, bb_middle, bb_lower = talib.BBANDS(prices, 
                                                        timeperiod=self.bollinger_period,
                                                        nbdevup=self.bollinger_std,
                                                        nbdevdn=self.bollinger_std)
            
            indicators['bollinger_bands'] = {
                'upper': self._safe_array_to_list(bb_upper),
                'middle': self._safe_array_to_list(bb_middle),
                'lower': self._safe_array_to_list(bb_lower),
                'current_upper': float(bb_upper[-1]) if not np.isnan(bb_upper[-1]) else 0.0,
                'current_middle': float(bb_middle[-1]) if not np.isnan(bb_middle[-1]) else 0.0,
                'current_lower': float(bb_lower[-1]) if not np.isnan(bb_lower[-1]) else 0.0,
                'squeeze': self._detect_bollinger_squeeze(bb_upper, bb_lower, bb_middle)
            }
            
            # Moving Averages (comprehensive set)
            indicators['moving_averages'] = {
                'sma_10': self._safe_talib_call(talib.SMA, prices, timeperiod=10),
                'sma_20': self._safe_talib_call(talib.SMA, prices, timeperiod=20),
                'sma_50': self._safe_talib_call(talib.SMA, prices, timeperiod=50),
                'sma_100': self._safe_talib_call(talib.SMA, prices, timeperiod=100),
                'sma_200': self._safe_talib_call(talib.SMA, prices, timeperiod=200),
                'ema_10': self._safe_talib_call(talib.EMA, prices, timeperiod=10),
                'ema_20': self._safe_talib_call(talib.EMA, prices, timeperiod=20),
                'ema_50': self._safe_talib_call(talib.EMA, prices, timeperiod=50),
                'ema_100': self._safe_talib_call(talib.EMA, prices, timeperiod=100),
                'ema_200': self._safe_talib_call(talib.EMA, prices, timeperiod=200)
            }
            
            # Momentum Indicators
            indicators['momentum'] = {
                'stoch_k': self._safe_talib_call(talib.STOCH, df['price'].values, df['price'].values, df['price'].values)[0],
                'stoch_d': self._safe_talib_call(talib.STOCH, df['price'].values, df['price'].values, df['price'].values)[1],
                'williams_r': self._safe_talib_call(talib.WILLR, df['price'].values, df['price'].values, df['price'].values),
                'roc': self._safe_talib_call(talib.ROC, prices, timeperiod=10),
                'momentum': self._safe_talib_call(talib.MOM, prices, timeperiod=10)
            }
            
            # Volume Indicators
            if len(volumes) > 0:
                indicators['volume'] = {
                    'volume_sma_20': self._safe_talib_call(talib.SMA, volumes, timeperiod=20),
                    'volume_ema_20': self._safe_talib_call(talib.EMA, volumes, timeperiod=20),
                    'obv': self._safe_talib_call(talib.OBV, prices, volumes),
                    'ad_line': self._calculate_ad_line(df),
                    'volume_ratio': self._calculate_volume_ratio(volumes)
                }
            
            # Volatility Indicators
            indicators['volatility'] = {
                'atr': self._safe_talib_call(talib.ATR, prices, prices, prices, timeperiod=14),
                'true_range': self._safe_talib_call(talib.TRANGE, prices, prices, prices),
                'volatility_ratio': self._calculate_volatility_ratio(prices)
            }
            
            # Trend Indicators
            indicators['trend'] = {
                'adx': self._safe_talib_call(talib.ADX, prices, prices, prices, timeperiod=14),
                'cci': self._safe_talib_call(talib.CCI, prices, prices, prices, timeperiod=14),
                'aroon_up': self._safe_talib_call(talib.AROON, prices, prices)[0],
                'aroon_down': self._safe_talib_call(talib.AROON, prices, prices)[1],
                'parabolic_sar': self._safe_talib_call(talib.SAR, prices, prices)
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def _safe_talib_call(self, func, *args, **kwargs):
        """Safely call TA-Lib function with error handling"""
        try:
            result = func(*args, **kwargs)
            if isinstance(result, tuple):
                return [self._safe_array_to_list(arr) for arr in result]
            else:
                return self._safe_array_to_list(result)
        except Exception as e:
            logger.warning(f"TA-Lib function {func.__name__} failed: {e}")
            return []
    
    def _safe_array_to_list(self, arr):
        """Safely convert numpy array to list"""
        try:
            if arr is None:
                return []
            return [float(x) if not np.isnan(x) else 0.0 for x in arr]
        except:
            return []
    
    def _generate_timeframe_signals(self, indicators: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive trading signals for timeframe"""
        signals = {
            'overall_signal': 'hold',
            'strength': 0.5,
            'individual_signals': {},
            'confluences': [],
            'divergences': []
        }
        
        try:
            current_price = float(df['price'].iloc[-1])
            
            # RSI Signals
            current_rsi = indicators.get('rsi', {}).get('current_rsi', 50)
            if current_rsi < self.rsi_oversold:
                signals['individual_signals']['rsi'] = 'strong_buy'
            elif current_rsi < 40:
                signals['individual_signals']['rsi'] = 'buy'
            elif current_rsi > self.rsi_overbought:
                signals['individual_signals']['rsi'] = 'strong_sell'
            elif current_rsi > 60:
                signals['individual_signals']['rsi'] = 'sell'
            else:
                signals['individual_signals']['rsi'] = 'hold'
            
            # MACD Signals
            macd_data = indicators.get('macd', {})
            current_macd = macd_data.get('current_macd', 0)
            current_signal = macd_data.get('current_signal', 0)
            current_hist = macd_data.get('current_histogram', 0)
            
            if current_macd > current_signal and current_hist > 0:
                signals['individual_signals']['macd'] = 'buy'
            elif current_macd < current_signal and current_hist < 0:
                signals['individual_signals']['macd'] = 'sell'
            else:
                signals['individual_signals']['macd'] = 'hold'
            
            # Bollinger Bands Signals
            bb_data = indicators.get('bollinger_bands', {})
            bb_upper = bb_data.get('current_upper', 0)
            bb_lower = bb_data.get('current_lower', 0)
            bb_middle = bb_data.get('current_middle', 0)
            
            if current_price < bb_lower:
                signals['individual_signals']['bollinger'] = 'buy'
            elif current_price > bb_upper:
                signals['individual_signals']['bollinger'] = 'sell'
            elif bb_data.get('squeeze', False):
                signals['individual_signals']['bollinger'] = 'breakout_pending'
            else:
                signals['individual_signals']['bollinger'] = 'hold'
            
            # Moving Average Signals
            ma_data = indicators.get('moving_averages', {})
            sma_20 = ma_data.get('sma_20', [])
            sma_50 = ma_data.get('sma_50', [])
            
            if len(sma_20) > 0 and len(sma_50) > 0:
                current_sma_20 = sma_20[-1] if sma_20[-1] != 0 else current_price
                current_sma_50 = sma_50[-1] if sma_50[-1] != 0 else current_price
                
                if current_sma_20 > current_sma_50 and current_price > current_sma_20:
                    signals['individual_signals']['ma_trend'] = 'buy'
                elif current_sma_20 < current_sma_50 and current_price < current_sma_20:
                    signals['individual_signals']['ma_trend'] = 'sell'
                else:
                    signals['individual_signals']['ma_trend'] = 'hold'
            
            # Calculate overall signal
            buy_signals = sum(1 for sig in signals['individual_signals'].values() 
                            if sig in ['buy', 'strong_buy'])
            sell_signals = sum(1 for sig in signals['individual_signals'].values() 
                             if sig in ['sell', 'strong_sell'])
            total_signals = len(signals['individual_signals'])
            
            if buy_signals > sell_signals and buy_signals >= total_signals * 0.6:
                signals['overall_signal'] = 'buy'
                signals['strength'] = min(0.9, 0.5 + (buy_signals / total_signals) * 0.4)
            elif sell_signals > buy_signals and sell_signals >= total_signals * 0.6:
                signals['overall_signal'] = 'sell'
                signals['strength'] = min(0.9, 0.5 + (sell_signals / total_signals) * 0.4)
            else:
                signals['overall_signal'] = 'hold'
                signals['strength'] = 0.5
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating timeframe signals: {e}")
            return signals
    
    def _generate_overall_recommendation(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall recommendation across all timeframes"""
        try:
            timeframe_weights = {
                '30m': 0.1,
                '1h': 0.15,
                '4h': 0.25,
                '1d': 0.35,
                '1w': 0.15
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            signal_counts = {'buy': 0, 'sell': 0, 'hold': 0}
            
            for timeframe, weight in timeframe_weights.items():
                if timeframe in analysis_results:
                    tf_data = analysis_results[timeframe]
                    signals = tf_data.get('signals', {})
                    overall_signal = signals.get('overall_signal', 'hold')
                    strength = signals.get('strength', 0.5)
                    
                    signal_counts[overall_signal] += weight
                    
                    # Convert signal to numeric score
                    if overall_signal == 'buy':
                        score = 0.5 + (strength * 0.5)
                    elif overall_signal == 'sell':
                        score = 0.5 - (strength * 0.5)
                    else:
                        score = 0.5
                    
                    weighted_score += score * weight
                    total_weight += weight
            
            if total_weight > 0:
                final_score = weighted_score / total_weight
            else:
                final_score = 0.5
            
            # Determine recommendation
            if final_score > 0.65:
                recommendation = 'strong_buy'
            elif final_score > 0.55:
                recommendation = 'buy'
            elif final_score < 0.35:
                recommendation = 'strong_sell'
            elif final_score < 0.45:
                recommendation = 'sell'
            else:
                recommendation = 'hold'
            
            return {
                'recommendation': recommendation,
                'confidence': abs(final_score - 0.5) * 2,  # 0 to 1 scale
                'score': round(final_score * 100, 1),
                'timeframe_consensus': signal_counts,
                'reasoning': self._generate_recommendation_reasoning(analysis_results, recommendation)
            }
            
        except Exception as e:
            logger.error(f"Error generating overall recommendation: {e}")
            return {
                'recommendation': 'hold',
                'confidence': 0.5,
                'score': 50.0,
                'timeframe_consensus': {'buy': 0, 'sell': 0, 'hold': 1},
                'reasoning': ['Error in analysis']
            }
    
    async def _get_coin_id(self, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID from symbol"""
        try:
            # Common mappings
            symbol_to_id = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'USDT': 'tether',
                'BNB': 'binancecoin',
                'SOL': 'solana',
                'USDC': 'usd-coin',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'ADA': 'cardano',
                'AVAX': 'avalanche-2',
                'LINK': 'chainlink',
                'DOT': 'polkadot',
                'MATIC': 'matic-network',
                'UNI': 'uniswap',
                'LTC': 'litecoin'
            }
            
            symbol_upper = symbol.upper()
            if symbol_upper in symbol_to_id:
                return symbol_to_id[symbol_upper]
            
            # Search via API if not in common mappings
            search_results = await coingecko_service.search_coins(symbol)
            if search_results:
                return search_results[0].get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting coin ID for {symbol}: {e}")
            return None
    
    def _get_coingecko_interval(self, timeframe: str) -> str:
        """Convert timeframe to CoinGecko interval"""
        mapping = {
            '30m': 'minutely',
            '1h': 'hourly', 
            '4h': 'hourly',
            '1d': 'daily',
            '1w': 'daily'
        }
        return mapping.get(timeframe, 'daily')
    
    def _calculate_comprehensive_score(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive technical analysis score"""
        try:
            scores = {
                'technical_score': 0.0,
                'momentum_score': 0.0,
                'trend_score': 0.0,
                'volume_score': 0.0,
                'volatility_score': 0.0,
                'overall_score': 0.0
            }
            
            # Calculate scores from each timeframe
            for timeframe, data in analysis_results.items():
                if 'signals' in data:
                    signals = data['signals']
                    strength = signals.get('strength', 0.5)
                    
                    # Weight by timeframe importance
                    weight = {'30m': 0.1, '1h': 0.15, '4h': 0.25, '1d': 0.35, '1w': 0.15}.get(timeframe, 0.2)
                    
                    scores['technical_score'] += strength * weight
            
            # Normalize scores
            scores['overall_score'] = min(100, max(0, scores['technical_score'] * 100))
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive score: {e}")
            return {'overall_score': 50.0}
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]["timestamp"]
        age = (datetime.now() - cached_time).total_seconds()
        
        return age < self.cache_ttl
    
    def _get_error_analysis(self) -> Dict[str, Any]:
        """Return error analysis structure"""
        return {
            "error": True,
            "message": "Analysis failed",
            "signals": {"overall_signal": "hold", "strength": 0.5}
        }
    
    def _get_insufficient_data_analysis(self) -> Dict[str, Any]:
        """Return insufficient data analysis structure"""
        return {
            "error": True,
            "message": "Insufficient data for analysis",
            "signals": {"overall_signal": "hold", "strength": 0.5}
        }


# Global instance
technical_analysis_service = RealTechnicalAnalysisService()

