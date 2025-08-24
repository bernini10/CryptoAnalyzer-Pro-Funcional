"""
Armazenamento global para dados do Pine Script
"""
import time
from typing import Dict, Any, Optional

# Armazenamento global dos dados do Pine Script
pine_signals_storage = {}

def store_pine_signal(symbol: str, data: Dict[str, Any]) -> None:
    """
    Armazenar sinal do Pine Script
    """
    symbol = symbol.upper().replace('USDT', '').replace('USD', '')
    pine_signals_storage[symbol] = {
        **data,
        'stored_at': time.time()
    }

def get_latest_pine_signal(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Obter último sinal do Pine Script para um símbolo
    """
    symbol = symbol.upper().replace('USDT', '').replace('USD', '')
    
    if symbol not in pine_signals_storage:
        return None
    
    data = pine_signals_storage[symbol]
    
    # Verificar se dados não são muito antigos (máximo 1 hora)
    if time.time() - data.get('stored_at', 0) > 3600:
        return None
    
    return data

def get_all_pine_signals() -> Dict[str, Any]:
    """
    Obter todos os sinais armazenados
    """
    return pine_signals_storage.copy()

