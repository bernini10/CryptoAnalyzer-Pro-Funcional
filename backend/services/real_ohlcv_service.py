"""
Serviço para coleta de dados OHLCV REAIS
Usa CoinGecko API para dados históricos necessários para análises técnicas
"""
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

class RealOHLCVService:
    """
    Serviço para coleta de dados OHLCV (Open, High, Low, Close, Volume) REAIS
    Necessário para cálculos técnicos precisos de RSI, MACD, Bollinger Bands
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
    async def get_session(self):
        """Obter sessão HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Fechar sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_cache_key(self, coin_id: str, days: int, interval: str) -> str:
        """Gerar chave de cache"""
        return f"ohlcv_{coin_id}_{days}_{interval}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verificar se cache é válido"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    async def get_ohlcv_data(self, coin_id: str, days: int = 30, interval: str = "hourly") -> Optional[pd.DataFrame]:
        """
        Obter dados OHLCV reais do CoinGecko
        
        Args:
            coin_id: ID da moeda no CoinGecko (bitcoin, ethereum, etc.)
            days: Número de dias históricos (1-365)
            interval: Intervalo dos dados (hourly, daily)
        
        Returns:
            DataFrame com colunas: timestamp, open, high, low, close, volume
        """
        try:
            cache_key = self._get_cache_key(coin_id, days, interval)
            
            # Verificar cache
            if self._is_cache_valid(cache_key):
                logger.info(f"📊 Usando dados OHLCV em cache para {coin_id}")
                return self.cache[cache_key]['data']
            
            logger.info(f"📊 Coletando dados OHLCV REAIS para {coin_id} ({days} dias, {interval})")
            
            session = await self.get_session()
            
            # URL para dados OHLCV do CoinGecko
            url = f"{self.base_url}/coins/{coin_id}/ohlc"
            params = {
                'vs_currency': 'usd',
                'days': days
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data:
                        logger.warning(f"⚠️ Dados OHLCV vazios para {coin_id}")
                        return None
                    
                    # Converter para DataFrame
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
                    
                    # Converter timestamp para datetime
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Adicionar volume (CoinGecko OHLC não inclui volume, buscar separadamente)
                    volume_data = await self._get_volume_data(coin_id, days)
                    if volume_data is not None:
                        df = df.merge(volume_data, on='timestamp', how='left')
                        df['volume'] = df['volume'].fillna(0)
                    else:
                        df['volume'] = 0
                    
                    # Garantir tipos numéricos
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Remover linhas com NaN
                    df = df.dropna()
                    
                    # Ordenar por timestamp
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    
                    logger.info(f"✅ Coletados {len(df)} pontos OHLCV para {coin_id}")
                    
                    # Armazenar em cache
                    self.cache[cache_key] = {
                        'data': df,
                        'timestamp': time.time()
                    }
                    
                    return df
                    
                else:
                    logger.error(f"❌ Erro na API CoinGecko OHLCV: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados OHLCV para {coin_id}: {e}")
            return None
    
    async def _get_volume_data(self, coin_id: str, days: int) -> Optional[pd.DataFrame]:
        """
        Obter dados de volume separadamente
        """
        try:
            session = await self.get_session()
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 90 else 'daily'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'total_volumes' in data:
                        volume_data = data['total_volumes']
                        df = pd.DataFrame(volume_data, columns=['timestamp', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        return df
                        
        except Exception as e:
            logger.warning(f"⚠️ Erro ao coletar dados de volume para {coin_id}: {e}")
        
        return None
    
    async def get_latest_price(self, coin_id: str) -> Optional[float]:
        """
        Obter preço atual (último close)
        """
        try:
            df = await self.get_ohlcv_data(coin_id, days=1)
            if df is not None and len(df) > 0:
                return float(df.iloc[-1]['close'])
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço atual de {coin_id}: {e}")
        
        return None
    
    async def get_price_history(self, coin_id: str, periods: int = 14) -> Optional[List[float]]:
        """
        Obter histórico de preços (closes) para cálculos técnicos
        
        Args:
            coin_id: ID da moeda
            periods: Número de períodos necessários
        
        Returns:
            Lista de preços de fechamento
        """
        try:
            # Buscar mais dados que o necessário para garantir períodos suficientes
            days = max(periods // 24 + 5, 7)  # Pelo menos 7 dias
            
            df = await self.get_ohlcv_data(coin_id, days=days)
            if df is not None and len(df) >= periods:
                # Retornar os últimos N períodos
                closes = df['close'].tail(periods).tolist()
                logger.info(f"📊 Histórico de {len(closes)} preços para {coin_id}")
                return closes
            else:
                logger.warning(f"⚠️ Dados insuficientes para {coin_id}: {len(df) if df is not None else 0} < {periods}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter histórico de preços de {coin_id}: {e}")
        
        return None

# Instância global
real_ohlcv_service = RealOHLCVService()

