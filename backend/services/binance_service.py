"""
Binance API Service - Dados OHLCV reais para análise técnica
"""
import aiohttp
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BinanceService:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> List[List]:
        """
        Get real OHLCV data from Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
            limit: Number of candles (max 1000)
        
        Returns:
            List of OHLCV data: [timestamp, open, high, low, close, volume, ...]
        """
        try:
            session = await self._get_session()
            
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            async with session.get(f"{self.base_url}/klines", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Binance: Got {len(data)} candles for {symbol} {interval}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Binance API error {response.status}: {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Binance klines error for {symbol}: {e}")
            return []
    
    async def get_ohlcv_dataframe(self, symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
        """
        Get OHLCV data as pandas DataFrame for technical analysis
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            klines = await self.get_klines(symbol, interval, limit)
            
            if not klines:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Keep only OHLCV columns and convert types
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
            
            # Convert to proper types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✅ Created OHLCV DataFrame for {symbol}: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"❌ OHLCV DataFrame error for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_24hr_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get 24hr ticker statistics"""
        try:
            session = await self._get_session()
            
            params = {'symbol': symbol}
            
            async with session.get(f"{self.base_url}/ticker/24hr", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'symbol': data['symbol'],
                        'price_change': float(data['priceChange']),
                        'price_change_percent': float(data['priceChangePercent']),
                        'last_price': float(data['lastPrice']),
                        'volume': float(data['volume']),
                        'quote_volume': float(data['quoteVolume']),
                        'high_price': float(data['highPrice']),
                        'low_price': float(data['lowPrice']),
                        'open_price': float(data['openPrice']),
                        'count': int(data['count'])
                    }
                else:
                    logger.error(f"❌ Binance 24hr ticker error {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Binance 24hr ticker error for {symbol}: {e}")
            return {}
    
    def symbol_to_binance(self, symbol: str) -> str:
        """
        Convert symbol to Binance format
        BTC -> BTCUSDT, ETH -> ETHUSDT, etc.
        """
        symbol = symbol.upper()
        
        # Special cases
        if symbol == 'USDT':
            return 'USDCUSDT'  # Use USDC as proxy for USDT
        
        # Most cryptos trade against USDT
        if not symbol.endswith('USDT'):
            symbol = f"{symbol}USDT"
            
        return symbol
    
    async def test_connection(self) -> bool:
        """Test Binance API connection"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/ping") as response:
                if response.status == 200:
                    logger.info("✅ Binance API connection successful")
                    return True
                else:
                    logger.error(f"❌ Binance ping failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Binance connection test failed: {e}")
            return False
    
    async def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information and trading pairs"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/exchangeInfo") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract active USDT pairs
                    usdt_pairs = []
                    for symbol_info in data.get('symbols', []):
                        if (symbol_info['status'] == 'TRADING' and 
                            symbol_info['symbol'].endswith('USDT') and
                            symbol_info['symbol'] != 'USDCUSDT'):  # Exclude USDC-USDT
                            usdt_pairs.append(symbol_info['symbol'])
                    
                    logger.info(f"✅ Found {len(usdt_pairs)} active USDT trading pairs")
                    return {
                        'timezone': data.get('timezone'),
                        'server_time': data.get('serverTime'),
                        'usdt_pairs': usdt_pairs[:100],  # Limit to first 100
                        'total_pairs': len(usdt_pairs)
                    }
                else:
                    logger.error(f"❌ Exchange info error: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Exchange info error: {e}")
            return {}

# Global instance
binance_service = BinanceService()

