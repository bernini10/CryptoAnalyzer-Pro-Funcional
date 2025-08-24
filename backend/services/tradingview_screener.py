"""
TradingView Screener Service - Dados automáticos de múltiplas criptomoedas
Coleta dados de 40+ pares automaticamente sem configuração manual
"""
import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)

class TradingViewScreenerService:
    def __init__(self):
        self.base_url = "https://scanner.tradingview.com"
        self.session = None
        self.last_update = None
        self.cached_data = {}
        self.update_interval = 60  # 1 minuto
        
        # Top 50 crypto symbols para monitorar
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
                'Content-Type': 'application/json',
                'Origin': 'https://www.tradingview.com',
                'Referer': 'https://www.tradingview.com/'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_crypto_screener_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get crypto data from TradingView Screener
        
        Args:
            symbols: List of symbols to get data for
            
        Returns:
            Dict with screener data
        """
        try:
            if symbols is None:
                symbols = self.crypto_symbols[:50]  # Top 50
            
            session = await self._get_session()
            
            # TradingView Screener payload
            payload = {
                "filter": [
                    {"left": "type", "operation": "equal", "right": "crypto"},
                    {"left": "subtype", "operation": "equal", "right": "spot"}
                ],
                "options": {"lang": "en"},
                "symbols": {
                    "query": {"types": []},
                    "tickers": [f"BINANCE:{symbol}" for symbol in symbols]
                },
                "columns": [
                    "name", "close", "change", "change_abs", "volume", "market_cap_basic",
                    "RSI", "RSI[1]", "MACD.macd", "MACD.signal", "MACD.hist",
                    "BB.upper", "BB.lower", "BB.basis", "Stoch.K", "Stoch.D",
                    "W.R", "CCI20", "ADX", "ADX+DI", "ADX-DI",
                    "VWAP", "P.SAR", "EMA12", "EMA26", "EMA50", "EMA200",
                    "SMA20", "SMA50", "SMA200", "ATR", "high|1D", "low|1D"
                ],
                "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
                "range": [0, len(symbols)]
            }
            
            url = f"{self.base_url}/crypto/scan"
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ TradingView Screener: Got data for {len(symbols)} symbols")
                    return self._process_screener_data(data)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ TradingView Screener error {response.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ TradingView Screener error: {e}")
            return {}
    
    def _process_screener_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Process raw screener data into structured format"""
        try:
            processed_data = {}
            
            if 'data' not in raw_data:
                return {}
            
            for row in raw_data['data']:
                if 'd' not in row:
                    continue
                    
                data = row['d']
                symbol = data[0] if len(data) > 0 else "UNKNOWN"
                
                # Extract symbol name (remove BINANCE: prefix)
                if ":" in symbol:
                    symbol = symbol.split(":")[1]
                
                # Map data to structured format
                processed_data[symbol] = {
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "price": data[1] if len(data) > 1 else 0,
                    "change_24h": data[2] if len(data) > 2 else 0,
                    "change_abs": data[3] if len(data) > 3 else 0,
                    "volume": data[4] if len(data) > 4 else 0,
                    "market_cap": data[5] if len(data) > 5 else 0,
                    
                    # Technical indicators
                    "rsi": data[6] if len(data) > 6 else 50,
                    "rsi_prev": data[7] if len(data) > 7 else 50,
                    "macd": data[8] if len(data) > 8 else 0,
                    "macd_signal": data[9] if len(data) > 9 else 0,
                    "macd_histogram": data[10] if len(data) > 10 else 0,
                    "bb_upper": data[11] if len(data) > 11 else 0,
                    "bb_lower": data[12] if len(data) > 12 else 0,
                    "bb_basis": data[13] if len(data) > 13 else 0,
                    "stoch_k": data[14] if len(data) > 14 else 50,
                    "stoch_d": data[15] if len(data) > 15 else 50,
                    "williams_r": data[16] if len(data) > 16 else -50,
                    "cci": data[17] if len(data) > 17 else 0,
                    "adx": data[18] if len(data) > 18 else 25,
                    "adx_plus_di": data[19] if len(data) > 19 else 25,
                    "adx_minus_di": data[20] if len(data) > 20 else 25,
                    "vwap": data[21] if len(data) > 21 else 0,
                    "sar": data[22] if len(data) > 22 else 0,
                    "ema_12": data[23] if len(data) > 23 else 0,
                    "ema_26": data[24] if len(data) > 24 else 0,
                    "ema_50": data[25] if len(data) > 25 else 0,
                    "ema_200": data[26] if len(data) > 26 else 0,
                    "sma_20": data[27] if len(data) > 27 else 0,
                    "sma_50": data[28] if len(data) > 28 else 0,
                    "sma_200": data[29] if len(data) > 29 else 0,
                    "atr": data[30] if len(data) > 30 else 0,
                    "high_1d": data[31] if len(data) > 31 else 0,
                    "low_1d": data[32] if len(data) > 32 else 0,
                    
                    # Calculated signals
                    "data_source": "TradingView Screener",
                    "quality": "REAL"
                }
                
                # Calculate composite signals
                processed_data[symbol] = self._calculate_signals(processed_data[symbol])
            
            logger.info(f"✅ Processed {len(processed_data)} symbols from screener")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error processing screener data: {e}")
            return {}
    
    def _calculate_signals(self, data: Dict) -> Dict:
        """Calculate buy/sell signals from technical indicators"""
        try:
            buy_signals = 0
            sell_signals = 0
            
            # RSI signals
            if data["rsi"] < 30:
                buy_signals += 1
            elif data["rsi"] > 70:
                sell_signals += 1
            
            # MACD signals
            if data["macd"] > data["macd_signal"]:
                buy_signals += 1
            else:
                sell_signals += 1
            
            # Bollinger Bands signals
            if data["price"] < data["bb_lower"]:
                buy_signals += 1
            elif data["price"] > data["bb_upper"]:
                sell_signals += 1
            
            # Stochastic signals
            if data["stoch_k"] < 20:
                buy_signals += 1
            elif data["stoch_k"] > 80:
                sell_signals += 1
            
            # Moving average signals
            if data["price"] > data["ema_50"]:
                buy_signals += 1
            else:
                sell_signals += 1
            
            # ADX trend strength
            trend_strength = "WEAK"
            if data["adx"] > 25:
                trend_strength = "STRONG"
                if data["adx_plus_di"] > data["adx_minus_di"]:
                    buy_signals += 1
                else:
                    sell_signals += 1
            
            # Final signal calculation
            signal_direction = "HOLD"
            if buy_signals > sell_signals:
                signal_direction = "BUY"
            elif sell_signals > buy_signals:
                signal_direction = "SELL"
            
            confidence = min(100, max(buy_signals, sell_signals) * 16.67)  # Max 6 signals = 100%
            
            # Add calculated fields
            data.update({
                "signal": signal_direction,
                "confidence": round(confidence, 1),
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "trend_strength": trend_strength,
                "recommendation": self._get_recommendation(signal_direction, confidence, trend_strength)
            })
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error calculating signals: {e}")
            return data
    
    def _get_recommendation(self, signal: str, confidence: float, trend_strength: str) -> str:
        """Get trading recommendation based on signals"""
        if signal == "BUY" and confidence > 60 and trend_strength == "STRONG":
            return "STRONG BUY"
        elif signal == "BUY" and confidence > 40:
            return "BUY"
        elif signal == "SELL" and confidence > 60 and trend_strength == "STRONG":
            return "STRONG SELL"
        elif signal == "SELL" and confidence > 40:
            return "SELL"
        else:
            return "HOLD"
    
    async def update_data(self) -> Dict[str, Any]:
        """Update screener data if needed"""
        try:
            now = datetime.now()
            
            # Check if update is needed
            if (self.last_update is None or 
                (now - self.last_update).total_seconds() > self.update_interval):
                
                logger.info("🔄 Updating TradingView Screener data...")
                
                # Get fresh data
                new_data = await self.get_crypto_screener_data()
                
                if new_data:
                    self.cached_data = new_data
                    self.last_update = now
                    logger.info(f"✅ Updated screener data: {len(new_data)} symbols")
                else:
                    logger.warning("⚠️ Failed to update screener data, using cache")
            
            return self.cached_data
            
        except Exception as e:
            logger.error(f"❌ Error updating screener data: {e}")
            return self.cached_data
    
    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get data for specific symbol"""
        try:
            data = await self.update_data()
            return data.get(symbol.upper(), {})
        except Exception as e:
            logger.error(f"❌ Error getting symbol data for {symbol}: {e}")
            return {}
    
    async def get_all_symbols_data(self) -> Dict[str, Any]:
        """Get data for all tracked symbols"""
        try:
            return await self.update_data()
        except Exception as e:
            logger.error(f"❌ Error getting all symbols data: {e}")
            return {}
    
    async def test_connection(self) -> bool:
        """Test TradingView Screener connection"""
        try:
            test_data = await self.get_crypto_screener_data(["BTCUSDT"])
            if test_data and "BTCUSDT" in test_data:
                logger.info("✅ TradingView Screener connection successful")
                return True
            else:
                logger.error("❌ TradingView Screener test failed")
                return False
        except Exception as e:
            logger.error(f"❌ TradingView Screener connection test failed: {e}")
            return False

# Global instance
tradingview_screener = TradingViewScreenerService()

