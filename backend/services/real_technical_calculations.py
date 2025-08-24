"""
Cálculos de indicadores técnicos REAIS
Implementação matemática precisa de RSI, MACD, Bollinger Bands
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RealTechnicalCalculations:
    """
    Classe para cálculos de indicadores técnicos REAIS
    Usa fórmulas matemáticas precisas com dados OHLCV históricos
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calcular RSI (Relative Strength Index) REAL
        
        Args:
            prices: Lista de preços de fechamento
            period: Período para cálculo (padrão 14)
        
        Returns:
            Valor RSI entre 0 e 100
        """
        try:
            if len(prices) < period + 1:
                logger.warning(f"⚠️ Dados insuficientes para RSI: {len(prices)} < {period + 1}")
                return None
            
            # Converter para pandas Series
            price_series = pd.Series(prices)
            
            # Calcular diferenças de preço
            delta = price_series.diff()
            
            # Separar ganhos e perdas
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calcular médias móveis dos ganhos e perdas
            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()
            
            # Calcular RS (Relative Strength)
            rs = avg_gains / avg_losses
            
            # Calcular RSI
            rsi = 100 - (100 / (1 + rs))
            
            # Retornar último valor
            last_rsi = rsi.iloc[-1]
            
            if pd.isna(last_rsi):
                logger.warning("⚠️ RSI calculado é NaN")
                return None
            
            logger.info(f"✅ RSI calculado: {last_rsi:.2f}")
            return float(last_rsi)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo RSI: {e}")
            return None
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict[str, float]]:
        """
        Calcular MACD (Moving Average Convergence Divergence) REAL
        
        Args:
            prices: Lista de preços de fechamento
            fast: Período EMA rápida (padrão 12)
            slow: Período EMA lenta (padrão 26)
            signal: Período linha de sinal (padrão 9)
        
        Returns:
            Dict com macd, signal, histogram
        """
        try:
            if len(prices) < slow + signal:
                logger.warning(f"⚠️ Dados insuficientes para MACD: {len(prices)} < {slow + signal}")
                return None
            
            # Converter para pandas Series
            price_series = pd.Series(prices)
            
            # Calcular EMAs
            ema_fast = price_series.ewm(span=fast).mean()
            ema_slow = price_series.ewm(span=slow).mean()
            
            # Calcular linha MACD
            macd_line = ema_fast - ema_slow
            
            # Calcular linha de sinal
            signal_line = macd_line.ewm(span=signal).mean()
            
            # Calcular histograma
            histogram = macd_line - signal_line
            
            # Obter últimos valores
            last_macd = macd_line.iloc[-1]
            last_signal = signal_line.iloc[-1]
            last_histogram = histogram.iloc[-1]
            
            if pd.isna(last_macd) or pd.isna(last_signal) or pd.isna(last_histogram):
                logger.warning("⚠️ MACD calculado contém NaN")
                return None
            
            result = {
                'macd': float(last_macd),
                'signal': float(last_signal),
                'histogram': float(last_histogram)
            }
            
            logger.info(f"✅ MACD calculado: {result['macd']:.4f}, Signal: {result['signal']:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo MACD: {e}")
            return None
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Optional[Dict[str, float]]:
        """
        Calcular Bollinger Bands REAIS
        
        Args:
            prices: Lista de preços de fechamento
            period: Período para média móvel (padrão 20)
            std_dev: Multiplicador do desvio padrão (padrão 2.0)
        
        Returns:
            Dict com upper, middle, lower
        """
        try:
            if len(prices) < period:
                logger.warning(f"⚠️ Dados insuficientes para Bollinger: {len(prices)} < {period}")
                return None
            
            # Converter para pandas Series
            price_series = pd.Series(prices)
            
            # Calcular média móvel simples
            sma = price_series.rolling(window=period).mean()
            
            # Calcular desvio padrão
            std = price_series.rolling(window=period).std()
            
            # Calcular bandas
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            # Obter últimos valores
            last_upper = upper_band.iloc[-1]
            last_middle = sma.iloc[-1]
            last_lower = lower_band.iloc[-1]
            
            if pd.isna(last_upper) or pd.isna(last_middle) or pd.isna(last_lower):
                logger.warning("⚠️ Bollinger Bands calculadas contêm NaN")
                return None
            
            result = {
                'upper': float(last_upper),
                'middle': float(last_middle),
                'lower': float(last_lower)
            }
            
            logger.info(f"✅ Bollinger calculado: Upper {result['upper']:.2f}, Lower {result['lower']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo Bollinger Bands: {e}")
            return None
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int = 20) -> Optional[float]:
        """
        Calcular Média Móvel Simples (SMA) REAL
        """
        try:
            if len(prices) < period:
                return None
            
            recent_prices = prices[-period:]
            sma = sum(recent_prices) / len(recent_prices)
            
            logger.info(f"✅ SMA{period} calculado: {sma:.2f}")
            return float(sma)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo SMA: {e}")
            return None
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> Optional[float]:
        """
        Calcular Média Móvel Exponencial (EMA) REAL
        """
        try:
            if len(prices) < period:
                return None
            
            price_series = pd.Series(prices)
            ema = price_series.ewm(span=period).mean()
            
            last_ema = ema.iloc[-1]
            if pd.isna(last_ema):
                return None
            
            logger.info(f"✅ EMA{period} calculado: {last_ema:.2f}")
            return float(last_ema)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo EMA: {e}")
            return None
    
    @staticmethod
    def analyze_trend(prices: List[float]) -> str:
        """
        Analisar tendência baseada nos preços
        """
        try:
            if len(prices) < 10:
                return "NEUTRAL"
            
            # Comparar últimos 5 com 5 anteriores
            recent = prices[-5:]
            previous = prices[-10:-5]
            
            recent_avg = sum(recent) / len(recent)
            previous_avg = sum(previous) / len(previous)
            
            change_pct = ((recent_avg - previous_avg) / previous_avg) * 100
            
            if change_pct > 2:
                return "BULLISH"
            elif change_pct < -2:
                return "BEARISH"
            else:
                return "NEUTRAL"
                
        except Exception:
            return "NEUTRAL"
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calcular volatilidade (desvio padrão dos retornos)
        """
        try:
            if len(prices) < period + 1:
                return None
            
            price_series = pd.Series(prices)
            returns = price_series.pct_change().dropna()
            
            if len(returns) < period:
                return None
            
            volatility = returns.tail(period).std() * 100  # Em percentual
            
            logger.info(f"✅ Volatilidade calculada: {volatility:.2f}%")
            return float(volatility)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de volatilidade: {e}")
            return None

# Instância global
real_calculations = RealTechnicalCalculations()

