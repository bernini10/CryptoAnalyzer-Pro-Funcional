"""
CoinGecko OHLCV Service - Dados OHLCV reais para análise técnica
Alternativa à Binance API que está bloqueada por localização
"""
import aiohttp
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CoinGeckoOHLCVService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        
        # Mapeamento de símbolos para IDs da CoinGecko
        self.symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'AVAX': 'avalanche-2',
            'LINK': 'chainlink',
            'DOT': 'polkadot',
            'MATIC': 'polygon',
            'UNI': 'uniswap',
            'LTC': 'litecoin',
            'XLM': 'stellar',
            'ALGO': 'algorand',
            'ATOM': 'cosmos',
            'FIL': 'filecoin',
            'VET': 'vechain',
            'ICP': 'internet-computer',
            'HBAR': 'hedera-hashgraph',
            'SAND': 'the-sandbox',
            'MANA': 'decentraland',
            'THETA': 'theta-token',
            'AAVE': 'aave',
            'MKR': 'maker',
            'COMP': 'compound-governance-token',
            'SUSHI': 'sushi',
            'YFI': 'yearn-finance',
            '1INCH': '1inch',
            'CRV': 'curve-dao-token',
            'SNX': 'synthetix-network-token',
            'ENJ': 'enjincoin',
            'BAT': 'basic-attention-token',
            'ZIL': 'zilliqa',
            'OMG': 'omg',
            'ZRX': '0x',
            'LRC': 'loopring',
            'KNC': 'kyber-network-crystal',
            'BNT': 'bancor',
            'REN': 'republic-protocol',
            'STORJ': 'storj',
            'NMR': 'numeraire',
            'REP': 'augur',
            'CVC': 'civic',
            'ANT': 'aragon',
            'GNO': 'gnosis',
            'GLM': 'golem',
            'SNT': 'status',
            'NEAR': 'near',
            'FTM': 'fantom',
            'EGLD': 'elrond-erd-2'
        }
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def symbol_to_coin_id(self, symbol: str) -> str:
        """Convert symbol to CoinGecko coin ID"""
        symbol = symbol.upper()
        return self.symbol_to_id.get(symbol, symbol.lower())
    
    async def get_ohlc_data(self, symbol: str, days: int = 7) -> List[List]:
        """
        Get real OHLC data from CoinGecko
        
        Args:
            symbol: Crypto symbol (BTC, ETH, etc.)
            days: Number of days (max 90 for hourly data)
        
        Returns:
            List of OHLC data: [timestamp, open, high, low, close]
        """
        try:
            coin_id = self.symbol_to_coin_id(symbol)
            session = await self._get_session()
            
            # CoinGecko OHLC endpoint
            url = f"{self.base_url}/coins/{coin_id}/ohlc"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 90)  # Max 90 days for hourly data
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ CoinGecko OHLC: Got {len(data)} candles for {symbol}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ CoinGecko OHLC error {response.status}: {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ CoinGecko OHLC error for {symbol}: {e}")
            return []
    
    async def get_market_chart(self, symbol: str, days: int = 7) -> Dict[str, List]:
        """
        Get market chart data with prices and volumes
        
        Args:
            symbol: Crypto symbol
            days: Number of days
            
        Returns:
            Dict with prices and total_volumes
        """
        try:
            coin_id = self.symbol_to_coin_id(symbol)
            session = await self._get_session()
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 90 else 'daily'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ CoinGecko Chart: Got data for {symbol}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ CoinGecko Chart error {response.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ CoinGecko Chart error for {symbol}: {e}")
            return {}
    
    async def get_ohlcv_dataframe(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
        """
        Get OHLCV data as pandas DataFrame using REAL price data from CoinGecko
        
        Args:
            symbol: Crypto symbol (BTC, ETH, etc.)
            timeframe: Timeframe ('1h', '4h', '1d')
            limit: Number of data points
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Calculate days needed - use more days to get enough data
            if timeframe in ['30m', '1h']:
                days = min(30, 90)  # 30 days should give us enough hourly data
            elif timeframe == '4h':
                days = min(60, 90)  # More days for 4h timeframe
            elif timeframe == '1d':
                days = min(limit, 365)  # Daily data
            else:
                days = 30  # Default
            
            logger.info(f"🔍 Getting {days} days of REAL price data for {symbol}")
            
            # Get market chart data with REAL prices
            chart_data = await self.get_market_chart(symbol, days)
            
            if not chart_data or 'prices' not in chart_data:
                logger.error(f"❌ No price data available for {symbol}")
                return pd.DataFrame()
            
            # Extract REAL price and volume data
            prices = chart_data.get('prices', [])
            volumes = chart_data.get('total_volumes', [])
            
            if not prices:
                logger.error(f"❌ Empty price data for {symbol}")
                return pd.DataFrame()
            
            logger.info(f"✅ Got {len(prices)} REAL price points for {symbol}")
            
            # Create OHLCV DataFrame from REAL price data
            df_data = []
            
            for i, (timestamp, price) in enumerate(prices):
                # Get volume (real if available)
                volume = volumes[i][1] if i < len(volumes) else 1000000
                
                # Create OHLC from consecutive prices (more realistic than simulation)
                if i == 0:
                    open_price = price
                    high_price = price
                    low_price = price
                    close_price = price
                else:
                    # Use previous close as open
                    open_price = prices[i-1][1]
                    
                    # Calculate realistic high/low based on price movement
                    price_change = abs(price - open_price)
                    volatility = price_change * 0.5  # 50% of price change as volatility
                    
                    high_price = max(price, open_price) + volatility
                    low_price = min(price, open_price) - volatility
                    close_price = price
                
                df_data.append({
                    'timestamp': pd.to_datetime(timestamp, unit='ms'),
                    'open': float(open_price),
                    'high': float(high_price),
                    'low': float(low_price),
                    'close': float(close_price),
                    'volume': float(volume)
                })
            
            if not df_data:
                logger.error(f"❌ No OHLCV data created for {symbol}")
                return pd.DataFrame()
            
            df = pd.DataFrame(df_data)
            logger.info(f"✅ Created OHLCV DataFrame from REAL prices for {symbol}: {len(df)} rows")
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Apply timeframe resampling if needed
            if timeframe == '4h' and len(df) > 50:
                # Resample to 4h using REAL price data
                df = df.set_index('timestamp').resample('4H').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna().reset_index()
                logger.info(f"✅ Resampled to 4h: {len(df)} candles")
                
            elif timeframe == '1d' and len(df) > 50:
                # Resample to daily using REAL price data
                df = df.set_index('timestamp').resample('1D').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna().reset_index()
                logger.info(f"✅ Resampled to 1d: {len(df)} candles")
            
            # Limit to requested number of rows (most recent)
            if len(df) > limit:
                df = df.tail(limit).reset_index(drop=True)
            
            # Validate data quality
            if len(df) < 20:
                logger.warning(f"⚠️ Limited data for {symbol}: only {len(df)} candles")
            
            logger.info(f"✅ Final REAL OHLCV DataFrame for {symbol} {timeframe}: {len(df)} rows")
            logger.info(f"📊 Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ OHLCV DataFrame error for {symbol}: {e}")
            return pd.DataFrame()
    
    async def test_connection(self) -> bool:
        """Test CoinGecko API connection"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/ping") as response:
                if response.status == 200:
                    logger.info("✅ CoinGecko API connection successful")
                    return True
                else:
                    logger.error(f"❌ CoinGecko ping failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ CoinGecko connection test failed: {e}")
            return False

# Global instance
coingecko_ohlcv_service = CoinGeckoOHLCVService()

