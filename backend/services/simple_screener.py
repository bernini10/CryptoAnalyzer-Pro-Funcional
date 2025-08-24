"""
Simple TradingView Screener - Versão simplificada que funciona
"""
import aiohttp
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SimpleScreenerService:
    def __init__(self):
        self.base_url = "https://scanner.tradingview.com"
        self.session = None
        
        # Top 50 crypto symbols
        self.crypto_symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
            "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
            "MATICUSDT", "UNIUSDT", "LTCUSDT", "XLMUSDT", "ALGOUSDT",
            "ATOMUSDT", "FILUSDT", "VETUSDT", "ICPUSDT", "HBARUSDT",
            "SANDUSDT", "MANAUSDT", "THETAUSDT", "AAVEUSDT", "MKRUSDT",
            "COMPUSDT", "SUSHIUSDT", "YFIUSDT", "1INCHUSDT", "CRVUSDT",
            "SNXUSDT", "ENJUSDT", "BATUSDT", "ZILUSDT", "OMGUSDT",
            "ZRXUSDT", "LRCUSDT", "KNCUSDT", "BNTUSDT", "RENUSDT",
            "STORJUSDT", "NMRUSDT", "REPUSDT", "CVCUSDT", "ANTUSDT",
            "GNOUSDT", "GLMUSDT", "SNTUSDT", "NEARUSDT", "FTMUSDT"
        ]
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_simple_crypto_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get basic crypto data from TradingView Screener
        Using only basic fields that are guaranteed to work
        """
        try:
            if symbols is None:
                symbols = self.crypto_symbols[:10]  # Start with top 10
            
            session = await self._get_session()
            
            # Simple payload with only basic fields
            payload = {
                "filter": [
                    {"left": "type", "operation": "equal", "right": "crypto"}
                ],
                "options": {"lang": "en"},
                "symbols": {
                    "query": {"types": []},
                    "tickers": [f"BINANCE:{symbol}" for symbol in symbols]
                },
                "columns": [
                    "name", "close", "change", "volume", "market_cap_basic",
                    "RSI", "MACD.macd", "MACD.signal"
                ],
                "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
                "range": [0, len(symbols)]
            }
            
            url = f"{self.base_url}/crypto/scan"
            
            logger.info(f"🔍 Requesting data for {len(symbols)} symbols")
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Got response from TradingView")
                    logger.info(f"📊 Response keys: {list(data.keys()) if data else 'No data'}")
                    
                    if 'data' in data and data['data']:
                        logger.info(f"📊 Data rows: {len(data['data'])}")
                        return self._process_simple_data(data)
                    else:
                        logger.warning("⚠️ No data in response")
                        return {}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ TradingView error {response.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Simple screener error: {e}")
            return {}
    
    def _process_simple_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Process raw data into simple format"""
        try:
            processed_data = {}
            
            for row in raw_data.get('data', []):
                if 'd' not in row:
                    continue
                    
                data = row['d']
                if len(data) < 3:
                    continue
                
                # Extract symbol name
                symbol = data[0] if data[0] else "UNKNOWN"
                if ":" in symbol:
                    symbol = symbol.split(":")[1]
                
                # Basic data mapping
                processed_data[symbol] = {
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "price": data[1] if len(data) > 1 and data[1] else 0,
                    "change_24h": data[2] if len(data) > 2 and data[2] else 0,
                    "volume": data[3] if len(data) > 3 and data[3] else 0,
                    "market_cap": data[4] if len(data) > 4 and data[4] else 0,
                    "rsi": data[5] if len(data) > 5 and data[5] else 50,
                    "macd": data[6] if len(data) > 6 and data[6] else 0,
                    "macd_signal": data[7] if len(data) > 7 and data[7] else 0,
                    
                    # Simple signals
                    "signal": self._get_simple_signal(
                        data[5] if len(data) > 5 and data[5] else 50,  # RSI
                        data[6] if len(data) > 6 and data[6] else 0,   # MACD
                        data[7] if len(data) > 7 and data[7] else 0    # MACD Signal
                    ),
                    "confidence": self._get_simple_confidence(
                        data[5] if len(data) > 5 and data[5] else 50,
                        data[6] if len(data) > 6 and data[6] else 0,
                        data[7] if len(data) > 7 and data[7] else 0
                    ),
                    "data_source": "TradingView Simple Screener",
                    "quality": "REAL"
                }
            
            logger.info(f"✅ Processed {len(processed_data)} symbols successfully")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error processing simple data: {e}")
            return {}
    
    def _get_simple_signal(self, rsi: float, macd: float, macd_signal: float) -> str:
        """Get simple buy/sell signal"""
        try:
            buy_signals = 0
            sell_signals = 0
            
            # RSI signals
            if rsi < 30:
                buy_signals += 1
            elif rsi > 70:
                sell_signals += 1
            
            # MACD signals
            if macd > macd_signal:
                buy_signals += 1
            else:
                sell_signals += 1
            
            if buy_signals > sell_signals:
                return "BUY"
            elif sell_signals > buy_signals:
                return "SELL"
            else:
                return "HOLD"
                
        except:
            return "HOLD"
    
    def _get_simple_confidence(self, rsi: float, macd: float, macd_signal: float) -> float:
        """Get simple confidence score"""
        try:
            confidence = 50  # Base confidence
            
            # RSI confidence
            if rsi < 20 or rsi > 80:
                confidence += 25
            elif rsi < 30 or rsi > 70:
                confidence += 15
            
            # MACD confidence
            macd_diff = abs(macd - macd_signal)
            if macd_diff > 50:
                confidence += 20
            elif macd_diff > 20:
                confidence += 10
            
            return min(100, confidence)
            
        except:
            return 50
    
    async def test_connection(self) -> bool:
        """Test simple screener connection"""
        try:
            logger.info("🧪 Testing simple screener connection")
            test_data = await self.get_simple_crypto_data(["BTCUSDT"])
            
            if test_data and "BTCUSDT" in test_data:
                logger.info("✅ Simple screener connection successful")
                logger.info(f"📊 Test data: {test_data['BTCUSDT']}")
                return True
            else:
                logger.error("❌ Simple screener test failed - no data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Simple screener test error: {e}")
            return False

# Global instance
simple_screener = SimpleScreenerService()

