"""
Telegram Service for CryptoAnalyzer Pro
Real implementation using Telegram Bot API
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramService:
    """Real Telegram Bot service for notifications"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
        if self.bot_token:
            logger.info(f"📱 Telegram service initialized with bot token: {self.bot_token[:10]}...")
        else:
            logger.warning("📱 Telegram bot token not found in environment variables")
        
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        return bool(self.bot_token)
    
    async def send_message(self, message: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Send message to Telegram"""
        if not self.is_configured():
            logger.warning("Telegram not configured - skipping message")
            return {"success": False, "error": "Not configured"}
        
        try:
            target_chat_id = chat_id or self.chat_id
            if not target_chat_id:
                # Try to get chat ID from recent updates
                target_chat_id = await self._get_chat_id()
                if not target_chat_id:
                    return {"success": False, "error": "No chat ID available"}
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": target_chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("ok"):
                        logger.info(f"Telegram message sent successfully to {target_chat_id}")
                        return {"success": True, "message_id": result["result"]["message_id"]}
                    else:
                        logger.error(f"Telegram API error: {result}")
                        return {"success": False, "error": result.get("description", "Unknown error")}
                        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_chat_id(self) -> Optional[str]:
        """Get chat ID from recent updates"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"limit": 1, "offset": -1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("ok") and result.get("result"):
                        updates = result["result"]
                        if updates:
                            chat_id = str(updates[0]["message"]["chat"]["id"])
                            logger.info(f"Found chat ID: {chat_id}")
                            return chat_id
                            
        except Exception as e:
            logger.error(f"Error getting chat ID: {e}")
        
        return None
    
    async def send_price_alert(self, symbol: str, price: float, change_24h: float, alert_type: str = "price") -> Dict[str, Any]:
        """Send price alert notification"""
        emoji = "🚀" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
        change_text = f"{change_24h:+.2f}%" if change_24h != 0 else "0.00%"
        
        message = f"""
🔔 <b>Alerta de Preço - CryptoAnalyzer Pro</b>

{emoji} <b>{symbol.upper()}</b>
💰 Preço: <b>${price:,.2f}</b>
📊 Variação 24h: <b>{change_text}</b>

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """.strip()
        
        return await self.send_message(message)
    
    async def send_technical_analysis(self, symbol: str, recommendation: str, score: int, confidence: float, signals: list) -> Dict[str, Any]:
        """Send technical analysis notification"""
        rec_emoji = "🟢" if recommendation == "BUY" else "🔴" if recommendation == "SELL" else "🟡"
        
        signals_text = "\n".join([f"• {signal}" for signal in signals[:3]])  # Top 3 signals
        
        message = f"""
📊 <b>Análise Técnica - CryptoAnalyzer Pro</b>

{rec_emoji} <b>{symbol.upper()}</b>
🎯 Recomendação: <b>{recommendation}</b>
📈 Score: <b>{score}/100</b>
🎯 Confiança: <b>{confidence:.0%}</b>

🔍 <b>Principais Sinais:</b>
{signals_text}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """.strip()
        
        return await self.send_message(message)
    
    async def send_altseason_alert(self, altseason_index: int, status: str, trend: str) -> Dict[str, Any]:
        """Send altseason alert notification"""
        status_emoji = "🚀" if "Alt Season" in status else "🔸" if "Mixed" in status else "₿"
        
        message = f"""
🌟 <b>Alt Season Update - CryptoAnalyzer Pro</b>

{status_emoji} <b>Status:</b> {status}
📊 <b>Índice:</b> {altseason_index}/100
📈 <b>Tendência:</b> {trend.title()}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """.strip()
        
        return await self.send_message(message)
    
    async def send_technical_analysis_alert(
        self, 
        symbol: str, 
        analysis_data: Dict[str, Any],
        ai_recommendation: str = None
    ) -> Dict[str, Any]:
        """Send technical analysis alert to Telegram"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            # Extract analysis data
            recommendation = analysis_data.get('recommendation', 'HOLD')
            confidence = analysis_data.get('confidence', 50)
            score = analysis_data.get('score', 50)
            signals = analysis_data.get('signals', [])
            
            # Create emoji based on recommendation
            emoji = "🟢" if recommendation == "BUY" else "🔴" if recommendation == "SELL" else "🟡"
            
            # Format message
            message = f"""
🚨 <b>ALERTA TÉCNICO - {symbol.upper()}</b> {emoji}

📊 <b>Análise Técnica:</b>
• Recomendação: <b>{recommendation}</b>
• Score: <b>{score}/100</b>
• Confiança: <b>{confidence}%</b>

🔍 <b>Sinais Detectados:</b>
{chr(10).join([f"• {signal}" for signal in signals[:5]]) if signals else "• Nenhum sinal forte"}

⏰ <b>Análise:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
📈 <b>Fonte:</b> Análise técnica real (RSI, MACD, Bollinger)

{f"🤖 <b>IA:</b> {ai_recommendation[:200]}..." if ai_recommendation else ""}

<i>CryptoAnalyzer Pro - Alertas Automáticos</i>
            """
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending technical analysis alert: {e}")
            return {"success": False, "error": str(e)}

    async def send_price_alert(
        self, 
        symbol: str, 
        current_price: float, 
        change_24h: float,
        alert_type: str = "price_change"
    ) -> Dict[str, Any]:
        """Send price alert to Telegram"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            # Determine emoji based on change
            if change_24h > 5:
                emoji = "🚀"
                status = "FORTE ALTA"
            elif change_24h > 2:
                emoji = "📈"
                status = "ALTA"
            elif change_24h < -5:
                emoji = "💥"
                status = "FORTE QUEDA"
            elif change_24h < -2:
                emoji = "📉"
                status = "QUEDA"
            else:
                emoji = "➡️"
                status = "ESTÁVEL"
            
            # Format price
            if current_price >= 1:
                price_str = f"${current_price:,.2f}"
            elif current_price >= 0.01:
                price_str = f"${current_price:.4f}"
            else:
                price_str = f"${current_price:.8f}"
            
            message = f"""
🔔 <b>ALERTA DE PREÇO - {symbol.upper()}</b> {emoji}

💰 <b>Preço Atual:</b> {price_str}
📊 <b>Variação 24h:</b> <b>{change_24h:+.2f}%</b>
📈 <b>Status:</b> {status}

⏰ <b>Horário:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
🎯 <b>Tipo:</b> {alert_type.replace('_', ' ').title()}

<i>CryptoAnalyzer Pro - Monitoramento Automático</i>
            """
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending price alert: {e}")
            return {"success": False, "error": str(e)}

    async def send_altseason_alert(
        self, 
        altseason_index: float, 
        bitcoin_dominance: float,
        top_altcoins: list = None
    ) -> Dict[str, Any]:
        """Send altcoin season alert to Telegram"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            # Determine status
            if altseason_index >= 75:
                emoji = "🌟"
                status = "FORTE ALT SEASON"
            elif altseason_index >= 60:
                emoji = "🚀"
                status = "ALT SEASON INICIANDO"
            elif altseason_index >= 40:
                emoji = "⚖️"
                status = "MERCADO MISTO"
            else:
                emoji = "🟠"
                status = "DOMINÂNCIA BTC"
            
            # Format top altcoins
            altcoins_text = ""
            if top_altcoins:
                altcoins_text = "\n🏆 <b>Top Performers:</b>\n"
                for coin in top_altcoins[:3]:
                    altcoins_text += f"• {coin.get('symbol', 'N/A')}: +{coin.get('vs_btc_7d', 0):.1f}% vs BTC\n"
            
            message = f"""
🌊 <b>ALERTA ALT SEASON</b> {emoji}

📊 <b>Índice Alt Season:</b> <b>{altseason_index:.1f}/100</b>
🟠 <b>Dominância BTC:</b> {bitcoin_dominance:.1f}%
📈 <b>Status:</b> {status}
{altcoins_text}
⏰ <b>Análise:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

<i>CryptoAnalyzer Pro - Monitoramento Alt Season</i>
            """
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending altseason alert: {e}")
            return {"success": False, "error": str(e)}

    async def send_test_message(self) -> Dict[str, Any]:
        """Test Telegram bot connection"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            url = f"{self.base_url}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("ok"):
                        bot_info = result["result"]
                        logger.info(f"Telegram bot connected: {bot_info['username']}")
                        return {
                            "success": True, 
                            "bot_username": bot_info["username"],
                            "bot_name": bot_info["first_name"]
                        }
                    else:
                        return {"success": False, "error": result.get("description", "Unknown error")}
                        
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return {"success": False, "error": str(e)}


# Global instance
telegram_service = TelegramService()

