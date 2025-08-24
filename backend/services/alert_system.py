"""
Sistema de Alertas Automatizado para CryptoAnalyzer Pro
Monitora condições de mercado e envia alertas via Telegram e Discord
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os

from .real_technical_analysis import real_technical_analysis
from .coingecko_service import coingecko_service
from .telegram_service import telegram_service
from .discord_service import discord_service
from .gemini_service import gemini_service

logger = logging.getLogger(__name__)


class AlertSystem:
    """Sistema automatizado de alertas baseado em análise técnica real"""
    
    def __init__(self):
        # Configurações do .env
        self.price_breakout_threshold = float(os.getenv('PRICE_BREAKOUT_THRESHOLD', 2.0))
        self.volume_spike_multiplier = float(os.getenv('VOLUME_SPIKE_MULTIPLIER', 3.0))
        self.alert_cooldown_minutes = int(os.getenv('ALERT_COOLDOWN_MINUTES', 15))
        self.alert_max_per_day = int(os.getenv('ALERT_MAX_PER_DAY', 100))
        
        # Alertas habilitados
        self.rsi_alert_enabled = os.getenv('RSI_ALERT_ENABLED', 'true').lower() == 'true'
        self.macd_alert_enabled = os.getenv('MACD_ALERT_ENABLED', 'true').lower() == 'true'
        self.altseason_alert_enabled = os.getenv('ALTSEASON_ALERT_ENABLED', 'true').lower() == 'true'
        
        # Controle de cooldown
        self.last_alerts = {}
        self.daily_alert_count = 0
        self.last_reset_date = datetime.now().date()
        
        # Símbolos para monitorar
        self.monitored_symbols = [
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'UNI',
            'MATIC', 'LTC', 'ATOM', 'NEAR', 'FTM', 'AAVE', 'SAND', 'MANA'
        ]
        
        self.running = False
    
    def _reset_daily_counter(self):
        """Reset contador diário de alertas"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_alert_count = 0
            self.last_reset_date = current_date
    
    def _can_send_alert(self, symbol: str, alert_type: str) -> bool:
        """Verifica se pode enviar alerta (cooldown e limites)"""
        self._reset_daily_counter()
        
        # Verificar limite diário
        if self.daily_alert_count >= self.alert_max_per_day:
            return False
        
        # Verificar cooldown
        alert_key = f"{symbol}_{alert_type}"
        if alert_key in self.last_alerts:
            time_since_last = datetime.now() - self.last_alerts[alert_key]
            if time_since_last.total_seconds() < (self.alert_cooldown_minutes * 60):
                return False
        
        return True
    
    def _mark_alert_sent(self, symbol: str, alert_type: str):
        """Marca alerta como enviado"""
        alert_key = f"{symbol}_{alert_type}"
        self.last_alerts[alert_key] = datetime.now()
        self.daily_alert_count += 1
    
    async def _send_alert(self, alert_type: str, symbol: str, data: Dict[str, Any]):
        """Envia alerta para todos os canais configurados"""
        try:
            results = {}
            
            # Telegram
            if telegram_service.is_configured():
                if alert_type == "technical_analysis":
                    result = await telegram_service.send_technical_analysis_alert(
                        symbol, data.get('analysis', {}), data.get('ai_recommendation')
                    )
                elif alert_type == "price_change":
                    result = await telegram_service.send_price_alert(
                        symbol, data.get('price', 0), data.get('change_24h', 0), alert_type
                    )
                elif alert_type == "altseason":
                    result = await telegram_service.send_altseason_alert(
                        data.get('altseason_index', 0), data.get('bitcoin_dominance', 0), 
                        data.get('top_altcoins', [])
                    )
                results['telegram'] = result
            
            # Discord
            if discord_service.is_configured():
                if alert_type == "technical_analysis":
                    result = await discord_service.send_technical_analysis_alert(
                        symbol, data.get('analysis', {}), data.get('ai_recommendation')
                    )
                elif alert_type == "price_change":
                    result = await discord_service.send_price_alert(
                        symbol, data.get('price', 0), data.get('change_24h', 0), alert_type
                    )
                elif alert_type == "altseason":
                    result = await discord_service.send_altseason_alert(
                        data.get('altseason_index', 0), data.get('bitcoin_dominance', 0), 
                        data.get('top_altcoins', [])
                    )
                results['discord'] = result
            
            logger.info(f"Alert sent for {symbol} ({alert_type}): {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error sending alert for {symbol}: {e}")
            return {"error": str(e)}
    
    async def process_tradingview_signal(self, signal_data: Dict[str, Any], ai_analysis: Optional[Dict] = None):
        """Processa sinal do TradingView e gera alertas automáticos"""
        try:
            symbol = signal_data.get('symbol', '').replace('.P', '').replace('USDT', '')
            confidence = signal_data.get('confidence', 0)
            recommendation = signal_data.get('signal', 'HOLD')
            
            # Só processar sinais com alta confiança
            if confidence < 70:
                logger.debug(f"Signal confidence too low for {symbol}: {confidence}%")
                return
            
            # Verificar se pode enviar alerta
            if not self._can_send_alert(symbol, "technical_analysis"):
                logger.debug(f"Alert cooldown active for {symbol}")
                return
            
            # Preparar dados do alerta
            alert_data = {
                'analysis': {
                    'symbol': symbol,
                    'recommendation': recommendation,
                    'confidence': confidence,
                    'score': int(confidence),
                    'signals': self._extract_signals_from_data(signal_data),
                    'indicators': {
                        'rsi': signal_data.get('rsi'),
                        'macd': signal_data.get('macd'),
                        'bb_position': self._get_bollinger_position(signal_data)
                    }
                },
                'ai_recommendation': ai_analysis.get('analysis', '') if ai_analysis else None,
                'reasons': [f"TradingView Signal: {recommendation}", f"Confidence: {confidence}%"]
            }
            
            # Enviar alerta
            results = await self._send_alert("technical_analysis", symbol, alert_data)
            
            if any(result.get('success') for result in results.values() if isinstance(result, dict)):
                self._mark_alert_sent(symbol, "technical_analysis")
                logger.info(f"✅ Alert sent for {symbol}: {recommendation} ({confidence}%)")
            else:
                logger.warning(f"⚠️ Failed to send alert for {symbol}: {results}")
            
        except Exception as e:
            logger.error(f"❌ Error processing TradingView signal: {e}")
    
    def _extract_signals_from_data(self, signal_data: Dict[str, Any]) -> List[str]:
        """Extrai sinais técnicos dos dados"""
        signals = []
        
        # RSI Signals
        rsi = signal_data.get('rsi')
        if rsi:
            if rsi < 30:
                signals.append("RSI Oversold")
            elif rsi > 70:
                signals.append("RSI Overbought")
            elif 40 <= rsi <= 60:
                signals.append("RSI Neutral Zone")
        
        # MACD Signals
        macd = signal_data.get('macd')
        macd_signal = signal_data.get('macd_signal')
        if macd and macd_signal:
            if macd > macd_signal:
                signals.append("MACD Bullish")
            else:
                signals.append("MACD Bearish")
        
        # Volume Signals
        volume_ratio = signal_data.get('volume_ratio')
        if volume_ratio and volume_ratio > 2:
            signals.append("Volume Spike")
        
        # Bollinger Bands
        bb_position = self._get_bollinger_position(signal_data)
        if bb_position:
            signals.append(f"BB {bb_position}")
        
        return signals[:5]  # Máximo 5 sinais
    
    def _get_bollinger_position(self, signal_data: Dict[str, Any]) -> Optional[str]:
        """Determina posição nas Bollinger Bands"""
        price = signal_data.get('price') or signal_data.get('close')
        bb_upper = signal_data.get('bb_upper')
        bb_lower = signal_data.get('bb_lower')
        bb_middle = signal_data.get('bb_middle')
        
        if not all([price, bb_upper, bb_lower, bb_middle]):
            return None
        
        if price > bb_upper:
            return "Breakout Up"
        elif price < bb_lower:
            return "Breakout Down"
        elif price > bb_middle:
            return "Upper Half"
        else:
            return "Lower Half"
    
    async def monitor_price_changes(self):
        """Monitora mudanças de preço e envia alertas"""
        try:
            for symbol in self.monitored_symbols:
                if not self._can_send_alert(symbol, "price_change"):
                    continue
                
                # Obter dados de preço
                coin_data = await coingecko_service.get_coin_data(symbol.lower())
                if not coin_data:
                    continue
                
                current_price = coin_data.get('current_price', 0)
                change_24h = coin_data.get('price_change_percentage_24h', 0)
                
                # Verificar se mudança é significativa
                if abs(change_24h) >= self.price_breakout_threshold:
                    alert_data = {
                        'price': current_price,
                        'change_24h': change_24h,
                        'market_cap': coin_data.get('market_cap', 0),
                        'volume_24h': coin_data.get('total_volume', 0)
                    }
                    
                    await self._send_alert("price_change", symbol, alert_data)
                    self._mark_alert_sent(symbol, "price_change")
                    
                    logger.info(f"Price alert sent for {symbol}: {change_24h:+.2f}%")
                
                # Pequena pausa entre símbolos
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error monitoring price changes: {e}")
    
    async def monitor_altseason(self):
        """Monitora Alt Season e envia alertas"""
        try:
            if not self.altseason_alert_enabled:
                return
            
            if not self._can_send_alert("ALTSEASON", "altseason"):
                return
            
            # Obter dados globais
            global_data = await coingecko_service.get_global_data()
            if not global_data:
                return
            
            bitcoin_dominance = global_data.get('market_cap_percentage', {}).get('btc', 0)
            
            # Calcular índice Alt Season (simplificado)
            altseason_index = max(0, min(100, 100 - bitcoin_dominance))
            
            # Determinar status
            if altseason_index >= 75:
                status = "Strong Alt Season"
            elif altseason_index >= 60:
                status = "Alt Season Starting"
            elif altseason_index >= 40:
                status = "Mixed Market"
            else:
                status = "Bitcoin Dominance"
            
            # Só alertar em mudanças significativas
            if altseason_index >= 60 or altseason_index <= 30:
                # Obter top altcoins
                top_altcoins = await self._get_top_altcoins_vs_btc()
                
                alert_data = {
                    'altseason_index': altseason_index,
                    'bitcoin_dominance': bitcoin_dominance,
                    'status': status,
                    'top_altcoins': top_altcoins
                }
                
                await self._send_alert("altseason", "ALTSEASON", alert_data)
                self._mark_alert_sent("ALTSEASON", "altseason")
                
                logger.info(f"Alt Season alert sent: {status} (Index: {altseason_index})")
                
        except Exception as e:
            logger.error(f"Error monitoring alt season: {e}")
    
    async def _get_top_altcoins_vs_btc(self) -> List[Dict]:
        """Obter top altcoins performance vs BTC"""
        try:
            top_altcoins = []
            
            for symbol in ['ETH', 'BNB', 'SOL', 'ADA', 'AVAX']:
                coin_data = await coingecko_service.get_coin_data(symbol.lower())
                if coin_data:
                    # Simular performance vs BTC (seria necessário dados históricos reais)
                    change_7d = coin_data.get('price_change_percentage_7d_in_currency', 0)
                    top_altcoins.append({
                        'symbol': symbol,
                        'vs_btc_7d': change_7d * 0.8  # Aproximação vs BTC
                    })
                
                await asyncio.sleep(0.5)
            
            return sorted(top_altcoins, key=lambda x: x['vs_btc_7d'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error getting top altcoins: {e}")
            return []
    
    async def start_monitoring(self):
        """Inicia monitoramento automático"""
        if self.running:
            logger.warning("Alert system already running")
            return
        
        self.running = True
        logger.info("🚨 Alert system started - Monitoring enabled")
        
        try:
            while self.running:
                # Monitorar mudanças de preço a cada 5 minutos
                await self.monitor_price_changes()
                
                # Monitorar Alt Season a cada 30 minutos
                if datetime.now().minute % 30 == 0:
                    await self.monitor_altseason()
                
                # Aguardar 5 minutos
                await asyncio.sleep(300)
                
        except Exception as e:
            logger.error(f"Error in alert monitoring loop: {e}")
        finally:
            self.running = False
            logger.info("🚨 Alert system stopped")
    
    async def stop_monitoring(self):
        """Para monitoramento automático"""
        self.running = False
        logger.info("🚨 Alert system stop requested")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Obter status do sistema de alertas"""
        self._reset_daily_counter()
        
        return {
            "running": self.running,
            "daily_alerts_sent": self.daily_alert_count,
            "daily_limit": self.alert_max_per_day,
            "cooldown_minutes": self.alert_cooldown_minutes,
            "monitored_symbols": len(self.monitored_symbols),
            "alerts_enabled": {
                "rsi": self.rsi_alert_enabled,
                "macd": self.macd_alert_enabled,
                "altseason": self.altseason_alert_enabled
            },
            "thresholds": {
                "price_breakout": self.price_breakout_threshold,
                "volume_spike": self.volume_spike_multiplier
            },
            "notifications": {
                "telegram": telegram_service.is_configured(),
                "discord": discord_service.is_configured()
            },
            "active_cooldowns": len(self.last_alerts),
            "last_reset": self.last_reset_date.isoformat()
        }


# Instância global
alert_system = AlertSystem()


# Manter compatibilidade com código existente
class AlertService:
    """Alert management service - Legacy compatibility"""
    
    def __init__(self):
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
        self.cooldown_tracker: Dict[str, datetime] = {}
        
    async def create_alert(self, alert_data: Dict[str, Any]) -> str:
        """Create a new alert"""
        try:
            alert_id = f"alert_{datetime.now().timestamp()}"
            
            alert = {
                "id": alert_id,
                "user_id": alert_data.get("user_id", "default"),
                "symbol": alert_data["symbol"],
                "type": alert_data["type"],
                "condition": alert_data["condition"],
                "target_value": alert_data["target_value"],
                "current_value": alert_data.get("current_value", 0),
                "message": alert_data.get("message", ""),
                "priority": alert_data.get("priority", "medium"),
                "is_active": True,
                "is_triggered": False,
                "created_at": datetime.now().isoformat(),
                "triggered_at": None
            }
            
            self.active_alerts[alert_id] = alert
            logger.info(f"Alert created: {alert_id} for {alert['symbol']}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        return list(self.active_alerts.values())
    
    async def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        try:
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
                logger.info(f"Alert deleted: {alert_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return False


# Global alert service instance para compatibilidade
alert_service = AlertService()

