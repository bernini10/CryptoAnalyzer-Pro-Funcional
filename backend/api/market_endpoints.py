"""
Endpoints para dados de mercado reais
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging
from services.coingecko_service import coingecko_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Lista dos 10 pares principais
MAIN_CRYPTOS = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'ripple', 'cardano', 'avalanche-2', 'polkadot', 'chainlink', 'uniswap']

@router.get("/market/global")
async def get_global_market_data():
    """
    Obter dados globais do mercado de criptomoedas
    """
    try:
        logger.info("🌍 Carregando dados globais do mercado...")
        
        # Buscar dados globais do CoinGecko
        global_data = await coingecko_service.get_global_data()
        
        if not global_data:
            raise HTTPException(status_code=500, detail="Falha ao carregar dados globais")
        
        logger.info("✅ Dados globais carregados com sucesso")
        
        return {
            "success": True,
            "data": global_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados globais: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/crypto/list")
async def get_crypto_list(limit: int = 10):
    """
    Obter lista das principais criptomoedas
    """
    try:
        logger.info(f"💰 Carregando lista de {limit} criptomoedas...")
        
        # Limitar aos 10 pares principais
        if limit > 10:
            limit = 10
            
        # Buscar dados dos cryptos principais
        crypto_data = await coingecko_service.get_crypto_list(MAIN_CRYPTOS[:limit])
        
        if not crypto_data:
            raise HTTPException(status_code=500, detail="Falha ao carregar dados das criptomoedas")
        
        logger.info(f"✅ {len(crypto_data)} criptomoedas carregadas com sucesso")
        
        return {
            "success": True,
            "data": crypto_data,
            "count": len(crypto_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar lista de cryptos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/crypto/overview")
async def get_crypto_overview():
    """
    Obter visão geral do mercado de criptomoedas
    """
    try:
        logger.info("📊 Carregando visão geral do mercado...")
        
        # Buscar dados globais
        global_data = await coingecko_service.get_global_data()
        
        if not global_data:
            raise HTTPException(status_code=500, detail="Falha ao carregar dados de overview")
        
        # Calcular índice Alt Season (100 - dominância BTC)
        btc_dominance = global_data.get('market_cap_percentage', {}).get('btc', 60)
        alt_season_index = round(100 - btc_dominance)
        
        overview_data = {
            "total_market_cap": global_data.get('total_market_cap', {}).get('usd', 0),
            "btc_dominance": btc_dominance,
            "alt_season_index": alt_season_index,
            "total_volume": global_data.get('total_volume', {}).get('usd', 0),
            "active_cryptocurrencies": global_data.get('active_cryptocurrencies', 0),
            "markets": global_data.get('markets', 0)
        }
        
        logger.info("✅ Visão geral carregada com sucesso")
        
        return {
            "success": True,
            "data": overview_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar overview: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/crypto/{symbol}/price")
async def get_crypto_price(symbol: str):
    """
    Obter preço atual de uma criptomoeda específica
    """
    try:
        logger.info(f"💲 Carregando preço de {symbol}...")
        
        # Mapear símbolo para ID do CoinGecko
        symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'AVAX': 'avalanche-2',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'UNI': 'uniswap'
        }
        
        crypto_id = symbol_to_id.get(symbol.upper())
        if not crypto_id:
            raise HTTPException(status_code=404, detail=f"Criptomoeda {symbol} não encontrada")
        
        # Buscar dados do crypto específico
        crypto_data = await coingecko_service.get_crypto_list([crypto_id])
        
        if not crypto_data or len(crypto_data) == 0:
            raise HTTPException(status_code=500, detail=f"Falha ao carregar dados de {symbol}")
        
        price_data = crypto_data[0]
        
        logger.info(f"✅ Preço de {symbol} carregado: ${price_data.get('current_price', 0)}")
        
        return {
            "success": True,
            "data": {
                "symbol": symbol.upper(),
                "name": price_data.get('name'),
                "current_price": price_data.get('current_price'),
                "price_change_24h": price_data.get('price_change_percentage_24h'),
                "market_cap": price_data.get('market_cap'),
                "volume_24h": price_data.get('total_volume')
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar preço de {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

