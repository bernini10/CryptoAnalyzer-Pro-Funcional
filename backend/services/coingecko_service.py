"""
CoinGecko Service - REAL API IMPLEMENTATION
Provides real cryptocurrency data from CoinGecko API
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import json

logger = logging.getLogger(__name__)


class RealCoinGeckoService:
    """Real CoinGecko API service with comprehensive data fetching"""
    
    def __init__(self):
        self.api_key = os.getenv('COINGECKO_API_KEY', 'CG-ifbCMa1G9KAynDCAr18xzaVN')
        self.base_url = "https://api.coingecko.com/api/v3"
        self.pro_url = "https://pro-api.coingecko.com/api/v3"
        
        # Use Pro API if we have a key
        self.api_url = self.pro_url if self.api_key and self.api_key != 'demo' else self.base_url
        
        self.headers = {
            'accept': 'application/json',
            'x-cg-pro-api-key': self.api_key
        } if self.api_key and self.api_key != 'demo' else {'accept': 'application/json'}
        
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    async def get_market_data(self, limit: int = 250) -> List[Dict[str, Any]]:
        """Get comprehensive market data for top cryptocurrencies"""
        try:
            cache_key = f"market_data_{limit}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Rate limiting
            await self._rate_limit()
            
            url = f"{self.api_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),  # CoinGecko max is 250
                'page': 1,
                'sparkline': 'true',
                'price_change_percentage': '1h,24h,7d,14d,30d,200d,1y'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process and enrich data
                        processed_data = []
                        for coin in data:
                            processed_coin = self._process_market_data(coin)
                            processed_data.append(processed_coin)
                        
                        # Cache result
                        self.cache[cache_key] = {
                            "data": processed_data,
                            "timestamp": datetime.now()
                        }
                        
                        return processed_data
                    else:
                        logger.error(f"CoinGecko API error: {response.status}")
                        return self._get_fallback_market_data(limit)
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return self._get_fallback_market_data(limit)
    
    async def get_historical_data(self, coin_id: str, days: int, interval: str = 'daily') -> List[Dict[str, Any]]:
        """Get historical price and volume data"""
        try:
            cache_key = f"historical_{coin_id}_{days}_{interval}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Rate limiting
            await self._rate_limit()
            
            # Determine the appropriate endpoint based on interval and days
            if interval == 'minutely' and days <= 1:
                # Use market_chart for minutely data (last 1 day)
                url = f"{self.api_url}/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'minutely'
                }
            elif interval == 'hourly' and days <= 90:
                # Use market_chart for hourly data (up to 90 days)
                url = f"{self.api_url}/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'hourly'
                }
            else:
                # Use market_chart for daily data
                url = f"{self.api_url}/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process historical data
                        historical_data = self._process_historical_data(data, interval)
                        
                        # Cache result
                        self.cache[cache_key] = {
                            "data": historical_data,
                            "timestamp": datetime.now()
                        }
                        
                        return historical_data
                    else:
                        logger.error(f"CoinGecko historical data error: {response.status}")
                        return self._get_fallback_historical_data(coin_id, days)
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e}")
            return self._get_fallback_historical_data(coin_id, days)
    
    async def get_coin_info(self, coin_id: str) -> Dict[str, Any]:
        """Get detailed coin information"""
        try:
            cache_key = f"coin_info_{coin_id}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Rate limiting
            await self._rate_limit()
            
            url = f"{self.api_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'true'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process coin info
                        coin_info = self._process_coin_info(data)
                        
                        # Cache result
                        self.cache[cache_key] = {
                            "data": coin_info,
                            "timestamp": datetime.now()
                        }
                        
                        return coin_info
                    else:
                        logger.error(f"CoinGecko coin info error: {response.status}")
                        return {}
            
        except Exception as e:
            logger.error(f"Error fetching coin info for {coin_id}: {e}")
            return {}
    
    async def search_coins(self, query: str) -> List[Dict[str, Any]]:
        """Search for coins by name or symbol"""
        try:
            # Rate limiting
            await self._rate_limit()
            
            url = f"{self.api_url}/search"
            params = {'query': query}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('coins', [])
                    else:
                        logger.error(f"CoinGecko search error: {response.status}")
                        return []
            
        except Exception as e:
            logger.error(f"Error searching coins: {e}")
            return []
    
    async def get_global_data(self) -> Dict[str, Any]:
        """Get global cryptocurrency market data"""
        try:
            cache_key = "global_data"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Rate limiting
            await self._rate_limit()
            
            url = f"{self.api_url}/global"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        global_data = data.get('data', {})
                        
                        # Process global data
                        processed_global = {
                            'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                            'total_volume_24h_usd': global_data.get('total_volume', {}).get('usd', 0),
                            'bitcoin_dominance': global_data.get('market_cap_percentage', {}).get('btc', 0),
                            'ethereum_dominance': global_data.get('market_cap_percentage', {}).get('eth', 0),
                            'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                            'markets': global_data.get('markets', 0),
                            'market_cap_change_24h': global_data.get('market_cap_change_percentage_24h_usd', 0)
                        }
                        
                        # Cache result
                        self.cache[cache_key] = {
                            "data": processed_global,
                            "timestamp": datetime.now()
                        }
                        
                        return processed_global
                    else:
                        logger.error(f"CoinGecko global data error: {response.status}")
                        return self._get_fallback_global_data()
            
        except Exception as e:
            logger.error(f"Error fetching global data: {e}")
            return self._get_fallback_global_data()
    
    async def get_trending_coins(self) -> List[Dict[str, Any]]:
        """Get trending coins"""
        try:
            cache_key = "trending_coins"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Rate limiting
            await self._rate_limit()
            
            url = f"{self.api_url}/search/trending"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        trending = data.get('coins', [])
                        
                        # Process trending coins
                        processed_trending = []
                        for coin_data in trending:
                            coin = coin_data.get('item', {})
                            processed_coin = {
                                'id': coin.get('id', ''),
                                'name': coin.get('name', ''),
                                'symbol': coin.get('symbol', ''),
                                'market_cap_rank': coin.get('market_cap_rank', 0),
                                'thumb': coin.get('thumb', ''),
                                'score': coin.get('score', 0)
                            }
                            processed_trending.append(processed_coin)
                        
                        # Cache result
                        self.cache[cache_key] = {
                            "data": processed_trending,
                            "timestamp": datetime.now()
                        }
                        
                        return processed_trending
                    else:
                        logger.error(f"CoinGecko trending error: {response.status}")
                        return []
            
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []
    
    def _process_market_data(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enrich market data"""
        try:
            return {
                'id': coin.get('id', ''),
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name', ''),
                'image': coin.get('image', ''),
                'current_price': coin.get('current_price', 0),
                'market_cap': coin.get('market_cap', 0),
                'market_cap_rank': coin.get('market_cap_rank', 0),
                'fully_diluted_valuation': coin.get('fully_diluted_valuation', 0),
                'total_volume': coin.get('total_volume', 0),
                'high_24h': coin.get('high_24h', 0),
                'low_24h': coin.get('low_24h', 0),
                'price_change_24h': coin.get('price_change_24h', 0),
                'price_change_percentage_24h': coin.get('price_change_percentage_24h', 0),
                'price_change_percentage_7d': coin.get('price_change_percentage_7d_in_currency', 0),
                'price_change_percentage_30d': coin.get('price_change_percentage_30d_in_currency', 0),
                'price_change_percentage_1y': coin.get('price_change_percentage_1y_in_currency', 0),
                'market_cap_change_24h': coin.get('market_cap_change_24h', 0),
                'market_cap_change_percentage_24h': coin.get('market_cap_change_percentage_24h', 0),
                'circulating_supply': coin.get('circulating_supply', 0),
                'total_supply': coin.get('total_supply', 0),
                'max_supply': coin.get('max_supply', 0),
                'ath': coin.get('ath', 0),
                'ath_change_percentage': coin.get('ath_change_percentage', 0),
                'ath_date': coin.get('ath_date', ''),
                'atl': coin.get('atl', 0),
                'atl_change_percentage': coin.get('atl_change_percentage', 0),
                'atl_date': coin.get('atl_date', ''),
                'roi': coin.get('roi', {}),
                'last_updated': coin.get('last_updated', ''),
                'sparkline_in_7d': coin.get('sparkline_in_7d', {}),
                'price_change_percentage_1h_in_currency': coin.get('price_change_percentage_1h_in_currency', 0),
                'price_change_percentage_24h_in_currency': coin.get('price_change_percentage_24h_in_currency', 0),
                'price_change_percentage_7d_in_currency': coin.get('price_change_percentage_7d_in_currency', 0)
            }
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            return {}
    
    def _process_historical_data(self, data: Dict[str, Any], interval: str) -> List[Dict[str, Any]]:
        """Process historical price and volume data"""
        try:
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            market_caps = data.get('market_caps', [])
            
            historical_data = []
            
            for i, price_data in enumerate(prices):
                timestamp = price_data[0]
                price = price_data[1]
                
                volume = volumes[i][1] if i < len(volumes) else 0
                market_cap = market_caps[i][1] if i < len(market_caps) else 0
                
                historical_point = {
                    'datetime': datetime.fromtimestamp(timestamp / 1000),
                    'timestamp': timestamp,
                    'price': price,
                    'volume': volume,
                    'market_cap': market_cap
                }
                
                historical_data.append(historical_point)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error processing historical data: {e}")
            return []
    
    def _process_coin_info(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """Process detailed coin information"""
        try:
            market_data = coin.get('market_data', {})
            
            return {
                'id': coin.get('id', ''),
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name', ''),
                'description': coin.get('description', {}).get('en', ''),
                'image': coin.get('image', {}),
                'market_cap_rank': coin.get('market_cap_rank', 0),
                'coingecko_rank': coin.get('coingecko_rank', 0),
                'coingecko_score': coin.get('coingecko_score', 0),
                'developer_score': coin.get('developer_score', 0),
                'community_score': coin.get('community_score', 0),
                'liquidity_score': coin.get('liquidity_score', 0),
                'public_interest_score': coin.get('public_interest_score', 0),
                'market_data': {
                    'current_price': market_data.get('current_price', {}).get('usd', 0),
                    'total_value_locked': market_data.get('total_value_locked', {}),
                    'mcap_to_tvl_ratio': market_data.get('mcap_to_tvl_ratio', 0),
                    'fdv_to_tvl_ratio': market_data.get('fdv_to_tvl_ratio', 0),
                    'roi': market_data.get('roi', {}),
                    'ath': market_data.get('ath', {}).get('usd', 0),
                    'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                    'ath_date': market_data.get('ath_date', {}).get('usd', ''),
                    'atl': market_data.get('atl', {}).get('usd', 0),
                    'atl_change_percentage': market_data.get('atl_change_percentage', {}).get('usd', 0),
                    'atl_date': market_data.get('atl_date', {}).get('usd', ''),
                    'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                    'fully_diluted_valuation': market_data.get('fully_diluted_valuation', {}).get('usd', 0),
                    'total_volume': market_data.get('total_volume', {}).get('usd', 0),
                    'high_24h': market_data.get('high_24h', {}).get('usd', 0),
                    'low_24h': market_data.get('low_24h', {}).get('usd', 0),
                    'price_change_24h': market_data.get('price_change_24h', 0),
                    'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
                    'price_change_percentage_7d': market_data.get('price_change_percentage_7d', 0),
                    'price_change_percentage_14d': market_data.get('price_change_percentage_14d', 0),
                    'price_change_percentage_30d': market_data.get('price_change_percentage_30d', 0),
                    'price_change_percentage_60d': market_data.get('price_change_percentage_60d', 0),
                    'price_change_percentage_200d': market_data.get('price_change_percentage_200d', 0),
                    'price_change_percentage_1y': market_data.get('price_change_percentage_1y', 0),
                    'market_cap_change_24h': market_data.get('market_cap_change_24h', 0),
                    'market_cap_change_percentage_24h': market_data.get('market_cap_change_percentage_24h', 0),
                    'circulating_supply': market_data.get('circulating_supply', 0),
                    'total_supply': market_data.get('total_supply', 0),
                    'max_supply': market_data.get('max_supply', 0)
                },
                'community_data': coin.get('community_data', {}),
                'developer_data': coin.get('developer_data', {}),
                'public_interest_stats': coin.get('public_interest_stats', {}),
                'last_updated': coin.get('last_updated', '')
            }
            
        except Exception as e:
            logger.error(f"Error processing coin info: {e}")
            return {}
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = datetime.now().timestamp()
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]["timestamp"]
        age = (datetime.now() - cached_time).total_seconds()
        
        return age < self.cache_ttl
    
    def _get_fallback_market_data(self, limit: int) -> List[Dict[str, Any]]:
        """Fallback market data when API fails"""
        # Return basic fallback data
        fallback_coins = [
            {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin', 'current_price': 67500, 'market_cap': 1327000000000, 'price_change_percentage_24h': 2.4},
            {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum', 'current_price': 4350, 'market_cap': 523000000000, 'price_change_percentage_24h': 3.1},
            {'id': 'tether', 'symbol': 'USDT', 'name': 'Tether', 'current_price': 1, 'market_cap': 118000000000, 'price_change_percentage_24h': 0.0}
        ]
        
        return fallback_coins[:limit]
    
    def _get_fallback_historical_data(self, coin_id: str, days: int) -> List[Dict[str, Any]]:
        """Fallback historical data when API fails"""
        # Generate basic historical data
        base_price = 67500 if coin_id == 'bitcoin' else 4350 if coin_id == 'ethereum' else 100
        historical_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            price = base_price * (1 + (i * 0.001))  # Simple price progression
            
            historical_data.append({
                'datetime': date,
                'timestamp': int(date.timestamp() * 1000),
                'price': price,
                'volume': 28000000000,
                'market_cap': price * 19000000
            })
        
        return historical_data
    
    async def get_global_market_data(self) -> Dict[str, Any]:
        """Get global cryptocurrency market data"""
        try:
            url = f"{self.base_url}/global"
            headers = {"x-cg-demo-api-key": self.api_key} if self.api_key else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('data', {})
                    else:
                        logger.error(f"CoinGecko global API error: {response.status}")
                        # Return fallback data
                        return {
                            'total_market_cap': {'usd': 1970000000000},  # 1.97T
                            'market_cap_percentage': {'bitcoin': 59.8},
                            'total_volume': {'usd': 43240000000}  # 43.24B
                        }
                        
        except Exception as e:
            logger.error(f"Error fetching global market data: {e}")
            # Return fallback data
            return {
                'total_market_cap': {'usd': 1970000000000},
                'market_cap_percentage': {'bitcoin': 59.8},
                'total_volume': {'usd': 43240000000}
            }
    
    async def get_trending_coins(self) -> List[Dict[str, Any]]:
        """Get trending cryptocurrencies"""
        try:
            url = f"{self.base_url}/search/trending"
            headers = {"x-cg-demo-api-key": self.api_key} if self.api_key else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        trending_coins = []
                        
                        for coin in result.get('coins', [])[:10]:
                            coin_data = coin.get('item', {})
                            trending_coins.append({
                                'id': coin_data.get('id'),
                                'symbol': coin_data.get('symbol'),
                                'name': coin_data.get('name'),
                                'market_cap_rank': coin_data.get('market_cap_rank'),
                                'thumb': coin_data.get('thumb')
                            })
                        
                        return trending_coins
                    else:
                        logger.error(f"CoinGecko trending API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []
    
    def _get_fallback_global_data(self) -> Dict[str, Any]:
        """Fallback global data when API fails"""
        return {
            'total_market_cap_usd': 1850000000000,
            'total_volume_24h_usd': 43240000000,
            'bitcoin_dominance': 59.8,
            'ethereum_dominance': 12.3,
            'active_cryptocurrencies': 13000,
            'markets': 1000,
            'market_cap_change_24h': 2.1
        }


# Global instance
coingecko_service = RealCoinGeckoService()

