"""
Scheduler Service - FIXED VERSION
Includes proper rate limiting and error handling
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
import aiohttp
import json

from core.config import settings
from .alert_system import alert_service

logger = logging.getLogger(__name__)

class SchedulerService:
    """Background scheduler with rate limiting"""
    
    def __init__(self):
        self.is_running = False
        self.tasks: List[asyncio.Task] = []
        self.session: aiohttp.ClientSession = None
        
        # Rate limiting configuration
        self.api_calls_per_minute = 50
        self.api_call_delay = 2.0  # 2 seconds between calls
        self.last_api_call = 0
        
    async def start(self):
        """Start the scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.session = aiohttp.ClientSession()
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._market_data_loop()),
            asyncio.create_task(self._alert_check_loop()),
            asyncio.create_task(self._technical_analysis_loop())
        ]
        
        logger.info("✅ Scheduler started with rate limiting")
    
    async def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info("✅ Scheduler stopped")
    
    async def _market_data_loop(self):
        """Market data collection loop with rate limiting"""
        while self.is_running:
            try:
                await self._collect_market_data()
                await asyncio.sleep(settings.MARKET_DATA_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in market data loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _alert_check_loop(self):
        """Alert checking loop"""
        while self.is_running:
            try:
                await self._check_alerts()
                await asyncio.sleep(60)  # Check alerts every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
                await asyncio.sleep(30)
    
    async def _technical_analysis_loop(self):
        """Technical analysis loop with rate limiting"""
        while self.is_running:
            try:
                await self._run_technical_analysis()
                await asyncio.sleep(settings.SCHEDULER_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in technical analysis loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_market_data(self):
        """Collect market data with rate limiting"""
        try:
            # Top cryptocurrencies to monitor
            symbols = ["bitcoin", "ethereum", "uniswap", "cardano", "bittensor"]
            
            market_data = {}
            
            for symbol in symbols:
                # Rate limiting: wait between API calls
                await self._rate_limit_delay()
                
                try:
                    data = await self._fetch_coin_data(symbol)
                    if data:
                        market_data[symbol.upper()] = {
                            "price": data.get("current_price", 0),
                            "volume": data.get("total_volume", 0),
                            "market_cap": data.get("market_cap", 0),
                            "price_change_24h": data.get("price_change_percentage_24h", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
            
            if market_data:
                logger.info(f"📊 Market data collected for {len(market_data)} symbols")
                
                # Store market data (in real implementation, save to database)
                self.latest_market_data = market_data
            
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")
    
    async def _fetch_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """Fetch data for a single coin with error handling"""
        try:
            url = f"{settings.COINGECKO_API_URL}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    logger.warning(f"Rate limited for {coin_id}, waiting...")
                    await asyncio.sleep(10)  # Wait longer for rate limit
                    return None
                
                if response.status == 200:
                    data = await response.json()
                    return data.get("market_data", {})
                else:
                    logger.warning(f"API error for {coin_id}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching {coin_id}: {e}")
            return None
    
    async def _rate_limit_delay(self):
        """Implement rate limiting delay"""
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.api_call_delay:
            wait_time = self.api_call_delay - time_since_last_call
            await asyncio.sleep(wait_time)
        
        self.last_api_call = asyncio.get_event_loop().time()
    
    async def _check_alerts(self):
        """Check alerts against latest market data"""
        try:
            if not hasattr(self, 'latest_market_data'):
                return
            
            triggered_alerts = await alert_service.check_alerts(self.latest_market_data)
            
            for alert in triggered_alerts:
                await alert_service.send_notification(alert)
                logger.info(f"🚨 Alert triggered: {alert['symbol']} - {alert['message']}")
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _run_technical_analysis(self):
        """Run technical analysis with rate limiting"""
        try:
            if not hasattr(self, 'latest_market_data'):
                return
            
            # Analyze top symbols with rate limiting
            symbols = list(self.latest_market_data.keys())[:10]  # Limit to 10 symbols
            
            for symbol in symbols:
                await self._rate_limit_delay()
                
                try:
                    # Mock technical analysis
                    analysis = {
                        "symbol": symbol,
                        "rsi": 65.5,
                        "macd": 0.25,
                        "bollinger_squeeze": True,
                        "volume_spike": False,
                        "recommendation": "hold",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    logger.debug(f"📈 Technical analysis for {symbol}: {analysis['recommendation']}")
                    
                except Exception as e:
                    logger.error(f"Error in technical analysis for {symbol}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error running technical analysis: {e}")


# Global scheduler instance
scheduler_service = SchedulerService()


async def start_scheduler():
    """Start the global scheduler"""
    await scheduler_service.start()


async def stop_scheduler():
    """Stop the global scheduler"""
    await scheduler_service.stop()

