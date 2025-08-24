"""
Cache Service para CryptoAnalyzer Pro
Sistema de cache otimizado com Redis e fallback em memória
"""

import os
import json
import logging
import asyncio
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import hashlib

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheService:
    """Serviço de cache otimizado com Redis e fallback em memória"""
    
    def __init__(self):
        # Configurações do .env
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        
        # TTL configurações
        self.market_data_ttl = int(os.getenv('CACHE_MARKET_DATA_TTL', 300))  # 5 minutos
        self.analysis_ttl = int(os.getenv('CACHE_ANALYSIS_TTL', 600))  # 10 minutos
        self.ml_prediction_ttl = int(os.getenv('CACHE_ML_PREDICTION_TTL', 1800))  # 30 minutos
        self.global_data_ttl = int(os.getenv('CACHE_GLOBAL_DATA_TTL', 900))  # 15 minutos
        
        # Redis connection
        self.redis = None
        self.redis_connected = False
        
        # Fallback cache em memória
        self.memory_cache = {}
        self.cache_timestamps = {}
        
        # Estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
    
    async def _connect_redis(self):
        """Conecta ao Redis"""
        if not REDIS_AVAILABLE or not self.cache_enabled:
            return False
        
        try:
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
            # Testar conexão
            await self.redis.ping()
            self.redis_connected = True
            logger.info("Redis connected successfully")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using memory cache fallback.")
            self.redis_connected = False
            return False
    
    def _generate_key(self, prefix: str, identifier: str, params: Dict = None) -> str:
        """Gera chave de cache consistente"""
        key_parts = [prefix, identifier]
        
        if params:
            # Ordenar parâmetros para consistência
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(params_hash)
        
        return ":".join(key_parts)
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if not self.cache_enabled:
            return None
        
        try:
            # Tentar Redis primeiro
            if self.redis_connected and self.redis:
                try:
                    value = await self.redis.get(key)
                    if value:
                        self.stats['hits'] += 1
                        return json.loads(value)
                except Exception as e:
                    logger.warning(f"Redis get error: {e}")
                    self.redis_connected = False
            
            # Fallback para cache em memória
            if key in self.memory_cache:
                timestamp = self.cache_timestamps.get(key)
                if timestamp and datetime.now() < timestamp:
                    self.stats['hits'] += 1
                    return self.memory_cache[key]
                else:
                    # Expirado
                    del self.memory_cache[key]
                    if key in self.cache_timestamps:
                        del self.cache_timestamps[key]
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats['errors'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Define valor no cache"""
        if not self.cache_enabled:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            
            # Tentar Redis primeiro
            if self.redis_connected and self.redis:
                try:
                    await self.redis.setex(key, ttl, serialized_value)
                    self.stats['sets'] += 1
                    return True
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")
                    self.redis_connected = False
            
            # Fallback para cache em memória
            self.memory_cache[key] = value
            self.cache_timestamps[key] = datetime.now() + timedelta(seconds=ttl)
            self.stats['sets'] += 1
            
            # Limpar cache em memória se muito grande
            if len(self.memory_cache) > 1000:
                await self._cleanup_memory_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            deleted = False
            
            # Redis
            if self.redis_connected and self.redis:
                try:
                    result = await self.redis.delete(key)
                    deleted = result > 0
                except Exception as e:
                    logger.warning(f"Redis delete error: {e}")
            
            # Memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
                deleted = True
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Remove chaves que correspondem ao padrão"""
        try:
            deleted_count = 0
            
            # Redis
            if self.redis_connected and self.redis:
                try:
                    keys = await self.redis.keys(pattern)
                    if keys:
                        deleted_count = await self.redis.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis clear pattern error: {e}")
            
            # Memory cache
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
                deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    async def _cleanup_memory_cache(self):
        """Limpa cache em memória expirado"""
        try:
            now = datetime.now()
            expired_keys = [
                key for key, timestamp in self.cache_timestamps.items()
                if timestamp < now
            ]
            
            for key in expired_keys:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                del self.cache_timestamps[key]
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Memory cache cleanup error: {e}")
    
    # Métodos específicos para diferentes tipos de dados
    
    async def get_market_data(self, symbol: str, params: Dict = None) -> Optional[Dict]:
        """Obtém dados de mercado do cache"""
        key = self._generate_key("market", symbol, params)
        return await self.get(key)
    
    async def set_market_data(self, symbol: str, data: Dict, params: Dict = None) -> bool:
        """Define dados de mercado no cache"""
        key = self._generate_key("market", symbol, params)
        return await self.set(key, data, self.market_data_ttl)
    
    async def get_analysis(self, symbol: str, timeframes: List[str] = None) -> Optional[Dict]:
        """Obtém análise técnica do cache"""
        params = {"timeframes": timeframes} if timeframes else None
        key = self._generate_key("analysis", symbol, params)
        return await self.get(key)
    
    async def set_analysis(self, symbol: str, data: Dict, timeframes: List[str] = None) -> bool:
        """Define análise técnica no cache"""
        params = {"timeframes": timeframes} if timeframes else None
        key = self._generate_key("analysis", symbol, params)
        return await self.set(key, data, self.analysis_ttl)
    
    async def get_ml_prediction(self, symbol: str) -> Optional[Dict]:
        """Obtém predição ML do cache"""
        key = self._generate_key("ml_prediction", symbol)
        return await self.get(key)
    
    async def set_ml_prediction(self, symbol: str, data: Dict) -> bool:
        """Define predição ML no cache"""
        key = self._generate_key("ml_prediction", symbol)
        return await self.set(key, data, self.ml_prediction_ttl)
    
    async def get_global_data(self) -> Optional[Dict]:
        """Obtém dados globais do cache"""
        key = self._generate_key("global", "market_data")
        return await self.get(key)
    
    async def set_global_data(self, data: Dict) -> bool:
        """Define dados globais no cache"""
        key = self._generate_key("global", "market_data")
        return await self.set(key, data, self.global_data_ttl)
    
    async def get_altseason_analysis(self) -> Optional[Dict]:
        """Obtém análise Alt Season do cache"""
        key = self._generate_key("altseason", "analysis")
        return await self.get(key)
    
    async def set_altseason_analysis(self, data: Dict) -> bool:
        """Define análise Alt Season no cache"""
        key = self._generate_key("altseason", "analysis")
        return await self.set(key, data, self.analysis_ttl)
    
    async def invalidate_symbol(self, symbol: str):
        """Invalida todos os caches de um símbolo"""
        patterns = [
            f"market:{symbol}*",
            f"analysis:{symbol}*",
            f"ml_prediction:{symbol}*"
        ]
        
        for pattern in patterns:
            await self.clear_pattern(pattern)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        redis_info = {}
        if self.redis_connected and self.redis:
            try:
                redis_info = await self.redis.info()
            except Exception as e:
                logger.warning(f"Error getting Redis info: {e}")
        
        return {
            "cache_enabled": self.cache_enabled,
            "redis_connected": self.redis_connected,
            "redis_url": self.redis_url,
            "stats": self.stats,
            "hit_rate_percent": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "ttl_settings": {
                "market_data": self.market_data_ttl,
                "analysis": self.analysis_ttl,
                "ml_prediction": self.ml_prediction_ttl,
                "global_data": self.global_data_ttl
            },
            "redis_info": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory_human": redis_info.get("used_memory_human", "N/A"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0)
            } if redis_info else {}
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de cache"""
        health = {
            "status": "healthy",
            "cache_enabled": self.cache_enabled,
            "redis_connected": self.redis_connected,
            "memory_cache_active": len(self.memory_cache) > 0,
            "errors": []
        }
        
        # Testar Redis se conectado
        if self.redis_connected and self.redis:
            try:
                await self.redis.ping()
            except Exception as e:
                health["status"] = "degraded"
                health["redis_connected"] = False
                health["errors"].append(f"Redis ping failed: {e}")
        
        # Testar operações básicas
        try:
            test_key = "health_check_test"
            test_value = {"timestamp": datetime.now().isoformat()}
            
            await self.set(test_key, test_value, 60)
            retrieved = await self.get(test_key)
            
            if retrieved != test_value:
                health["status"] = "unhealthy"
                health["errors"].append("Cache set/get test failed")
            
            await self.delete(test_key)
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["errors"].append(f"Cache operations test failed: {e}")
        
        return health
    
    async def initialize(self):
        """Inicializa o serviço de cache"""
        if self.cache_enabled:
            await self._connect_redis()
            logger.info(f"Cache service initialized. Redis: {self.redis_connected}")
        else:
            logger.info("Cache service disabled")


# Instância global
cache_service = CacheService()

