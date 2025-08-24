"""
Real Technical Indicators - Cálculos matemáticos 100% reais
Baseado em dados OHLCV históricos da Binance API
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RealTechnicalIndicators:
    """
    Classe para cálculos matemáticos reais de indicadores técnicos
    Todos os cálculos são baseados em fórmulas matemáticas padrão da indústria
    """
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula RSI (Relative Strength Index) real
        
        Fórmula: RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        """
        try:
            if len(prices) < period + 1:
                return pd.Series([50] * len(prices), index=prices.index)
            
            # Calcular mudanças de preço
            delta = prices.diff()
            
            # Separar ganhos e perdas
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calcular médias móveis exponenciais
            avg_gains = gains.ewm(span=period, adjust=False).mean()
            avg_losses = losses.ewm(span=period, adjust=False).mean()
            
            # Evitar divisão por zero
            rs = avg_gains / avg_losses.replace(0, np.inf)
            rsi = 100 - (100 / (1 + rs))
            
            # Preencher valores NaN
            rsi = rsi.fillna(50)
            
            logger.debug(f"✅ RSI calculated: min={rsi.min():.2f}, max={rsi.max():.2f}, last={rsi.iloc[-1]:.2f}")
            return rsi
            
        except Exception as e:
            logger.error(f"❌ RSI calculation error: {e}")
            return pd.Series([50] * len(prices), index=prices.index)
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calcula MACD (Moving Average Convergence Divergence) real
        
        MACD Line = EMA(fast) - EMA(slow)
        Signal Line = EMA(MACD Line, signal)
        Histogram = MACD Line - Signal Line
        """
        try:
            if len(prices) < slow + signal:
                zeros = pd.Series([0] * len(prices), index=prices.index)
                return {
                    'macd': zeros,
                    'signal': zeros,
                    'histogram': zeros
                }
            
            # Calcular EMAs
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            
            # MACD Line
            macd_line = ema_fast - ema_slow
            
            # Signal Line
            signal_line = macd_line.ewm(span=signal).mean()
            
            # Histogram
            histogram = macd_line - signal_line
            
            result = {
                'macd': macd_line.fillna(0),
                'signal': signal_line.fillna(0),
                'histogram': histogram.fillna(0)
            }
            
            logger.debug(f"✅ MACD calculated: MACD={macd_line.iloc[-1]:.4f}, Signal={signal_line.iloc[-1]:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ MACD calculation error: {e}")
            zeros = pd.Series([0] * len(prices), index=prices.index)
            return {'macd': zeros, 'signal': zeros, 'histogram': zeros}
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calcula Bollinger Bands reais
        
        Middle Band = SMA(period)
        Upper Band = Middle Band + (std_dev * Standard Deviation)
        Lower Band = Middle Band - (std_dev * Standard Deviation)
        """
        try:
            if len(prices) < period:
                middle = pd.Series([prices.mean()] * len(prices), index=prices.index)
                return {
                    'upper': middle,
                    'middle': middle,
                    'lower': middle
                }
            
            # Middle Band (SMA)
            middle_band = prices.rolling(window=period).mean()
            
            # Standard Deviation
            std = prices.rolling(window=period).std()
            
            # Upper and Lower Bands
            upper_band = middle_band + (std_dev * std)
            lower_band = middle_band - (std_dev * std)
            
            result = {
                'upper': upper_band.fillna(method='bfill'),
                'middle': middle_band.fillna(method='bfill'),
                'lower': lower_band.fillna(method='bfill')
            }
            
            logger.debug(f"✅ Bollinger Bands calculated: Upper={upper_band.iloc[-1]:.2f}, Lower={lower_band.iloc[-1]:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Bollinger Bands calculation error: {e}")
            middle = pd.Series([prices.mean()] * len(prices), index=prices.index)
            return {'upper': middle, 'middle': middle, 'lower': middle}
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
        """Calcula Simple Moving Average real"""
        try:
            sma = prices.rolling(window=period).mean()
            return sma.fillna(method='bfill')
        except Exception as e:
            logger.error(f"❌ SMA calculation error: {e}")
            return pd.Series([prices.mean()] * len(prices), index=prices.index)
    
    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        """Calcula Exponential Moving Average real"""
        try:
            ema = prices.ewm(span=period).mean()
            return ema.fillna(method='bfill')
        except Exception as e:
            logger.error(f"❌ EMA calculation error: {e}")
            return pd.Series([prices.mean()] * len(prices), index=prices.index)
    
    @staticmethod
    def detect_signals(df: pd.DataFrame, rsi: pd.Series, macd_data: Dict, bb_data: Dict) -> List[str]:
        """
        Detecta sinais técnicos reais baseados em cálculos matemáticos
        """
        signals = []
        
        try:
            if len(df) < 2:
                return signals
            
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            current_rsi = rsi.iloc[-1]
            current_macd = macd_data['macd'].iloc[-1]
            current_signal = macd_data['signal'].iloc[-1]
            prev_macd = macd_data['macd'].iloc[-2] if len(macd_data['macd']) > 1 else current_macd
            prev_signal = macd_data['signal'].iloc[-2] if len(macd_data['signal']) > 1 else current_signal
            
            # RSI Signals
            if current_rsi < 30:
                signals.append("RSI Oversold")
            elif current_rsi > 70:
                signals.append("RSI Overbought")
            
            # MACD Signals
            if current_macd > current_signal and prev_macd <= prev_signal:
                signals.append("MACD Bullish Crossover")
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signals.append("MACD Bearish Crossover")
            
            # Bollinger Bands Signals
            upper_band = bb_data['upper'].iloc[-1]
            lower_band = bb_data['lower'].iloc[-1]
            
            if current_price > upper_band:
                signals.append("Price Above Upper Band")
            elif current_price < lower_band:
                signals.append("Price Below Lower Band")
            
            # Volume Analysis
            if len(df) >= 20:
                avg_volume = df['volume'].tail(20).mean()
                current_volume = df['volume'].iloc[-1]
                
                if current_volume > avg_volume * 2:
                    signals.append("High Volume Spike")
                elif current_volume < avg_volume * 0.5:
                    signals.append("Low Volume")
            
            # Price Movement
            price_change_pct = ((current_price - prev_price) / prev_price) * 100
            
            if price_change_pct > 5:
                signals.append("Strong Bullish Move")
            elif price_change_pct < -5:
                signals.append("Strong Bearish Move")
            
            logger.debug(f"✅ Detected {len(signals)} real signals: {signals}")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Signal detection error: {e}")
            return []
    
    @staticmethod
    def calculate_score_and_recommendation(df: pd.DataFrame, rsi: pd.Series, macd_data: Dict, bb_data: Dict, signals: List[str]) -> Tuple[int, str, float]:
        """
        Calcula score e recomendação baseados em análise técnica real
        
        Returns:
            Tuple[score, recommendation, confidence]
        """
        try:
            if len(df) < 2:
                return 50, "HOLD", 50.0
            
            current_rsi = rsi.iloc[-1]
            current_macd = macd_data['macd'].iloc[-1]
            current_signal = macd_data['signal'].iloc[-1]
            current_price = df['close'].iloc[-1]
            middle_band = bb_data['middle'].iloc[-1]
            
            # Score base
            score = 50
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI Analysis
            if current_rsi < 30:
                score += 15  # Oversold = bullish
                bullish_signals += 1
            elif current_rsi > 70:
                score -= 15  # Overbought = bearish
                bearish_signals += 1
            elif 40 <= current_rsi <= 60:
                score += 5   # Neutral zone = slight positive
            
            # MACD Analysis
            if current_macd > current_signal:
                score += 10  # MACD above signal = bullish
                bullish_signals += 1
            else:
                score -= 10  # MACD below signal = bearish
                bearish_signals += 1
            
            # Bollinger Bands Analysis
            if current_price > middle_band:
                score += 8   # Price above middle = bullish
                bullish_signals += 1
            else:
                score -= 8   # Price below middle = bearish
                bearish_signals += 1
            
            # Signals Analysis
            for signal in signals:
                if any(word in signal.lower() for word in ['bullish', 'oversold', 'above', 'spike']):
                    score += 3
                    bullish_signals += 1
                elif any(word in signal.lower() for word in ['bearish', 'overbought', 'below']):
                    score -= 3
                    bearish_signals += 1
            
            # Limit score
            score = max(0, min(100, score))
            
            # Determine recommendation
            if score >= 65:
                recommendation = "BUY"
            elif score <= 35:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            # Calculate confidence based on signal strength
            total_signals = bullish_signals + bearish_signals
            if total_signals == 0:
                confidence = 50.0
            else:
                signal_strength = abs(bullish_signals - bearish_signals) / total_signals
                confidence = 50 + (signal_strength * 40)  # 50-90% range
            
            confidence = max(50.0, min(95.0, confidence))
            
            logger.debug(f"✅ Real analysis: Score={score}, Rec={recommendation}, Conf={confidence:.1f}%")
            return score, recommendation, confidence
            
        except Exception as e:
            logger.error(f"❌ Score calculation error: {e}")
            return 50, "HOLD", 50.0

# Global instance
real_indicators = RealTechnicalIndicators()

