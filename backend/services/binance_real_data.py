"""
Serviço Binance para dados OHLCV 100% REAIS
Coleta dados históricos diretamente da exchange Binance
"""
import asyncio
import aiohttp
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BinanceRealDataService:
    """
    Serviço para coleta de dados OHLCV 100% REAIS da Binance
    Sem simulações - apenas dados reais de exchange
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Mapeamento de símbolos
        self.symbol_mapping = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'BNB': 'BNBUSDT',
            'SOL': 'SOLUSDT',
            'XRP': 'XRPUSDT',
            'ADA': 'ADAUSDT',
            'AVAX': 'AVAXUSDT',
            'DOT': 'DOTUSDT',
            'LINK': 'LINKUSDT',
            'UNI': 'UNIUSDT'
        }
        
        # Mapeamento de intervalos
        self.interval_mapping = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
    
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
    
    def _get_cache_key(self, symbol: str, interval: str, limit: int) -> str:
        """Gerar chave de cache"""
        return f"binance_{symbol}_{interval}_{limit}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verificar se cache é válido"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Obter preço atual REAL da Binance
        """
        try:
            if symbol not in self.symbol_mapping:
                logger.error(f"❌ Símbolo {symbol} não suportado")
                return None
            
            binance_symbol = self.symbol_mapping[symbol]
            
            session = await self.get_session()
            url = f"{self.base_url}/ticker/price"
            params = {'symbol': binance_symbol}
            
            logger.info(f"💰 Buscando preço REAL de {symbol} na Binance...")
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data['price'])
                    
                    logger.info(f"✅ Preço REAL de {symbol}: ${price:.2f}")
                    return price
                else:
                    logger.error(f"❌ Erro na Binance API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço REAL de {symbol}: {e}")
            return None
    
    async def get_ohlcv_data(self, symbol: str, interval: str = "1h", limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Obter dados OHLCV históricos 100% REAIS da Binance
        
        Args:
            symbol: Símbolo da crypto (BTC, ETH, etc.)
            interval: Intervalo (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            limit: Número de candles (max 1000)
        
        Returns:
            DataFrame com dados REAIS: timestamp, open, high, low, close, volume
        """
        try:
            cache_key = self._get_cache_key(symbol, interval, limit)
            
            # Verificar cache
            if self._is_cache_valid(cache_key):
                logger.info(f"📊 Usando dados OHLCV REAIS em cache para {symbol}")
                return self.cache[cache_key]['data']
            
            if symbol not in self.symbol_mapping:
                logger.error(f"❌ Símbolo {symbol} não suportado")
                return None
            
            if interval not in self.interval_mapping:
                logger.error(f"❌ Intervalo {interval} não suportado")
                return None
            
            binance_symbol = self.symbol_mapping[symbol]
            binance_interval = self.interval_mapping[interval]
            
            session = await self.get_session()
            url = f"{self.base_url}/klines"
            params = {
                'symbol': binance_symbol,
                'interval': binance_interval,
                'limit': min(limit, 1000)  # Binance max limit
            }
            
            logger.info(f"📊 Coletando dados OHLCV REAIS da Binance: {symbol} {interval} ({limit} candles)")
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data:
                        logger.error(f"❌ Dados OHLCV vazios para {symbol}")
                        return None
                    
                    # Converter dados da Binance para DataFrame
                    ohlcv_data = []
                    for candle in data:
                        ohlcv_data.append({
                            'timestamp': pd.to_datetime(candle[0], unit='ms'),
                            'open': float(candle[1]),
                            'high': float(candle[2]),
                            'low': float(candle[3]),
                            'close': float(candle[4]),
                            'volume': float(candle[5])
                        })
                    
                    df = pd.DataFrame(ohlcv_data)
                    
                    # Verificar dados
                    if len(df) == 0:
                        logger.error(f"❌ DataFrame vazio para {symbol}")
                        return None
                    
                    # Ordenar por timestamp
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    
                    logger.info(f"✅ Dados OHLCV REAIS coletados: {len(df)} candles para {symbol}")
                    logger.info(f"📈 Preço atual REAL: ${df.iloc[-1]['close']:.2f}")
                    logger.info(f"📊 Range de preços: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
                    
                    # Armazenar em cache
                    self.cache[cache_key] = {
                        'data': df,
                        'timestamp': time.time()
                    }
                    
                    return df
                    
                else:
                    logger.error(f"❌ Erro na Binance API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados OHLCV REAIS de {symbol}: {e}")
            return None
    
    async def get_24h_stats(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Obter estatísticas 24h REAIS da Binance
        """
        try:
            if symbol not in self.symbol_mapping:
                return None
            
            binance_symbol = self.symbol_mapping[symbol]
            
            session = await self.get_session()
            url = f"{self.base_url}/ticker/24hr"
            params = {'symbol': binance_symbol}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'price_change': float(data['priceChange']),
                        'price_change_percent': float(data['priceChangePercent']),
                        'high_price': float(data['highPrice']),
                        'low_price': float(data['lowPrice']),
                        'volume': float(data['volume']),
                        'quote_volume': float(data['quoteVolume']),
                        'open_price': float(data['openPrice']),
                        'close_price': float(data['lastPrice'])
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats 24h de {symbol}: {e}")
        
        return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obter preços REAIS de múltiplos símbolos
        """
        try:
            logger.info(f"💰 Buscando preços REAIS de {len(symbols)} símbolos na Binance...")
            
            # Preparar símbolos para Binance
            binance_symbols = []
            symbol_map = {}
            
            for symbol in symbols:
                if symbol in self.symbol_mapping:
                    binance_symbol = self.symbol_mapping[symbol]
                    binance_symbols.append(binance_symbol)
                    symbol_map[binance_symbol] = symbol
            
            if not binance_symbols:
                return {}
            
            session = await self.get_session()
            url = f"{self.base_url}/ticker/price"
            
            # Buscar todos os preços de uma vez
            async with session.get(url) as response:
                if response.status == 200:
                    all_prices = await response.json()
                    
                    prices = {}
                    for price_data in all_prices:
                        binance_symbol = price_data['symbol']
                        if binance_symbol in symbol_map:
                            symbol = symbol_map[binance_symbol]
                            prices[symbol] = float(price_data['price'])
                    
                    logger.info(f"✅ Preços REAIS obtidos para {len(prices)} símbolos")
                    return prices
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter múltiplos preços REAIS: {e}")
            return {}

# Instância global
binance_real_service = BinanceRealDataService()

