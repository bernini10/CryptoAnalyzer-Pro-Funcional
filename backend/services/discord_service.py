"""
Discord Service for CryptoAnalyzer Pro
Real implementation using Discord Webhooks
"""

import os
import logging
import aiohttp
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DiscordService:
    """Real Discord Webhook service for notifications"""
    
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        if self.webhook_url:
            logger.info(f"💬 Discord service initialized with webhook: {self.webhook_url[:50]}...")
        else:
            logger.warning("💬 Discord webhook URL not found in environment variables")
        
    def is_configured(self) -> bool:
        """Check if Discord is properly configured"""
        return bool(self.webhook_url and self.webhook_url.startswith('https://discord.com/api/webhooks/'))
    
    async def send_message(self, content: str = None, embeds: List[Dict] = None) -> Dict[str, Any]:
        """Send message to Discord via webhook"""
        if not self.is_configured():
            logger.warning("Discord not configured - skipping message")
            return {"success": False, "error": "Not configured"}
        
        try:
            payload = {}
            
            if content:
                payload["content"] = content
            
            if embeds:
                payload["embeds"] = embeds
            
            if not payload:
                return {"success": False, "error": "No content provided"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status in [200, 204]:
                        logger.info("Discord message sent successfully")
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        logger.error(f"Discord webhook error: {response.status} - {error_text}")
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_price_alert(self, symbol: str, price: float, change_24h: float, alert_type: str = "price") -> Dict[str, Any]:
        """Send price alert notification"""
        color = 0x00ff00 if change_24h > 0 else 0xff0000 if change_24h < 0 else 0xffff00
        emoji = "🚀" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
        change_text = f"{change_24h:+.2f}%" if change_24h != 0 else "0.00%"
        
        embed = {
            "title": f"{emoji} Alerta de Preço - {symbol.upper()}",
            "description": f"**Preço:** ${price:,.2f}\n**Variação 24h:** {change_text}",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "CryptoAnalyzer Pro",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/6001/6001527.png"
            },
            "fields": [
                {
                    "name": "Símbolo",
                    "value": symbol.upper(),
                    "inline": True
                },
                {
                    "name": "Tipo de Alerta",
                    "value": alert_type.title(),
                    "inline": True
                }
            ]
        }
        
        return await self.send_message(embeds=[embed])
    
    async def send_technical_analysis(self, symbol: str, recommendation: str, score: int, confidence: float, signals: list) -> Dict[str, Any]:
        """Send technical analysis notification"""
        color = 0x00ff00 if recommendation == "BUY" else 0xff0000 if recommendation == "SELL" else 0xffff00
        rec_emoji = "🟢" if recommendation == "BUY" else "🔴" if recommendation == "SELL" else "🟡"
        
        signals_text = "\n".join([f"• {signal}" for signal in signals[:5]])  # Top 5 signals
        
        embed = {
            "title": f"{rec_emoji} Análise Técnica - {symbol.upper()}",
            "description": f"**Recomendação:** {recommendation}",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "CryptoAnalyzer Pro - Análise Técnica Real",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/6001/6001527.png"
            },
            "fields": [
                {
                    "name": "📈 Score",
                    "value": f"{score}/100",
                    "inline": True
                },
                {
                    "name": "🎯 Confiança",
                    "value": f"{confidence:.0%}",
                    "inline": True
                },
                {
                    "name": "🔍 Principais Sinais",
                    "value": signals_text or "Nenhum sinal detectado",
                    "inline": False
                }
            ]
        }
        
        return await self.send_message(embeds=[embed])
    
    async def send_altseason_alert(self, altseason_index: int, status: str, trend: str, top_performers: list = None) -> Dict[str, Any]:
        """Send altseason alert notification"""
        if "Alt Season" in status:
            color = 0x00ff00
            emoji = "🚀"
        elif "Mixed" in status:
            color = 0xffff00
            emoji = "🔸"
        else:
            color = 0x0099ff
            emoji = "₿"
        
        description = f"**Status:** {status}\n**Tendência:** {trend.title()}"
        
        embed = {
            "title": f"{emoji} Alt Season Update",
            "description": description,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "CryptoAnalyzer Pro - Alt Season Tracker",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/6001/6001527.png"
            },
            "fields": [
                {
                    "name": "📊 Índice Alt Season",
                    "value": f"{altseason_index}/100",
                    "inline": True
                }
            ]
        }
        
        if top_performers:
            performers_text = "\n".join([
                f"• {perf['symbol']}: {perf['change']:+.1f}%" 
                for perf in top_performers[:5]
            ])
            embed["fields"].append({
                "name": "🏆 Top Performers",
                "value": performers_text,
                "inline": False
            })
        
        return await self.send_message(embeds=[embed])
    
    async def send_system_status(self, status: str, services: Dict[str, str], features: Dict[str, Any]) -> Dict[str, Any]:
        """Send system status notification"""
        color = 0x00ff00 if status == "healthy" else 0xff0000
        
        services_text = "\n".join([
            f"• {service}: {'✅' if status == 'operational' else '❌'} {status.title()}"
            for service, status in services.items()
        ])
        
        features_text = "\n".join([
            f"• {feature}: {'✅' if enabled else '❌'}"
            for feature, enabled in features.items()
            if isinstance(enabled, bool)
        ])
        
        embed = {
            "title": f"🔧 System Status - {status.title()}",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "CryptoAnalyzer Pro - System Monitor",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/6001/6001527.png"
            },
            "fields": [
                {
                    "name": "🛠️ Services",
                    "value": services_text,
                    "inline": True
                },
                {
                    "name": "⚡ Features",
                    "value": features_text,
                    "inline": True
                }
            ]
        }
        
        return await self.send_message(embeds=[embed])
    
    async def send_technical_analysis_alert(
        self, 
        symbol: str, 
        analysis_data: Dict[str, Any],
        ai_recommendation: str = None
    ) -> Dict[str, Any]:
        """Send technical analysis alert to Discord"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            # Extract analysis data
            recommendation = analysis_data.get('recommendation', 'HOLD')
            confidence = analysis_data.get('confidence', 50)
            score = analysis_data.get('score', 50)
            signals = analysis_data.get('signals', [])
            
            # Determine color based on recommendation
            color = 0x00FF00 if recommendation == "BUY" else 0xFF0000 if recommendation == "SELL" else 0xFFFF00
            
            # Create embed
            embed = {
                "title": f"🚨 ALERTA TÉCNICO - {symbol.upper()}",
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "📊 Recomendação",
                        "value": f"**{recommendation}**",
                        "inline": True
                    },
                    {
                        "name": "🎯 Score",
                        "value": f"**{score}/100**",
                        "inline": True
                    },
                    {
                        "name": "📈 Confiança",
                        "value": f"**{confidence}%**",
                        "inline": True
                    },
                    {
                        "name": "🔍 Sinais Detectados",
                        "value": "\n".join([f"• {signal}" for signal in signals[:5]]) if signals else "• Nenhum sinal forte",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "CryptoAnalyzer Pro - Análise Técnica Real"
                }
            }
            
            # Add AI recommendation if available
            if ai_recommendation:
                embed["fields"].append({
                    "name": "🤖 Análise IA",
                    "value": ai_recommendation[:1000] + "..." if len(ai_recommendation) > 1000 else ai_recommendation,
                    "inline": False
                })
            
            return await self.send_message(embeds=[embed])
            
        except Exception as e:
            logger.error(f"Error sending technical analysis alert to Discord: {e}")
            return {"success": False, "error": str(e)}

    async def send_price_alert(
        self, 
        symbol: str, 
        current_price: float, 
        change_24h: float,
        alert_type: str = "price_change"
    ) -> Dict[str, Any]:
        """Send price alert to Discord"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            # Determine color and status
            if change_24h > 5:
                color = 0x00FF00  # Green
                status = "🚀 FORTE ALTA"
            elif change_24h > 2:
                color = 0x90EE90  # Light Green
                status = "📈 ALTA"
            elif change_24h < -5:
                color = 0xFF0000  # Red
                status = "💥 FORTE QUEDA"
            elif change_24h < -2:
                color = 0xFF6B6B  # Light Red
                status = "📉 QUEDA"
            else:
                color = 0xFFFF00  # Yellow
                status = "➡️ ESTÁVEL"
            
            # Format price
            if current_price >= 1:
                price_str = f"${current_price:,.2f}"
            elif current_price >= 0.01:
                price_str = f"${current_price:.4f}"
            else:
                price_str = f"${current_price:.8f}"
            
            # Create embed
            embed = {
                "title": f"🔔 ALERTA DE PREÇO - {symbol.upper()}",
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "💰 Preço Atual",
                        "value": price_str,
                        "inline": True
                    },
                    {
                        "name": "📊 Variação 24h",
                        "value": f"**{change_24h:+.2f}%**",
                        "inline": True
                    },
                    {
                        "name": "📈 Status",
                        "value": status,
                        "inline": True
                    },
                    {
                        "name": "🎯 Tipo de Alerta",
                        "value": alert_type.replace('_', ' ').title(),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "CryptoAnalyzer Pro - Monitoramento Automático"
                }
            }
            
            return await self.send_message(embeds=[embed])
            
        except Exception as e:
            logger.error(f"Error sending price alert to Discord: {e}")
            return {"success": False, "error": str(e)}

    async def send_altseason_alert(
        self, 
        altseason_index: float, 
        bitcoin_dominance: float,
        top_altcoins: list = None
    ) -> Dict[str, Any]:
        """Send altcoin season alert to Discord"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        try:
            # Determine color and status
            if altseason_index >= 75:
                color = 0x00FF00  # Green
                status = "🌟 FORTE ALT SEASON"
            elif altseason_index >= 60:
                color = 0x90EE90  # Light Green
                status = "🚀 ALT SEASON INICIANDO"
            elif altseason_index >= 40:
                color = 0xFFFF00  # Yellow
                status = "⚖️ MERCADO MISTO"
            else:
                color = 0xFF6B00  # Orange
                status = "🟠 DOMINÂNCIA BTC"
            
            # Create fields
            fields = [
                {
                    "name": "📊 Índice Alt Season",
                    "value": f"**{altseason_index:.1f}/100**",
                    "inline": True
                },
                {
                    "name": "🟠 Dominância BTC",
                    "value": f"{bitcoin_dominance:.1f}%",
                    "inline": True
                },
                {
                    "name": "📈 Status",
                    "value": status,
                    "inline": True
                }
            ]
            
            # Add top altcoins if available
            if top_altcoins:
                altcoins_text = "\n".join([
                    f"• **{coin.get('symbol', 'N/A')}**: +{coin.get('vs_btc_7d', 0):.1f}% vs BTC"
                    for coin in top_altcoins[:5]
                ])
                fields.append({
                    "name": "🏆 Top Performers vs BTC",
                    "value": altcoins_text,
                    "inline": False
                })
            
            # Create embed
            embed = {
                "title": "🌊 ALERTA ALT SEASON",
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "fields": fields,
                "footer": {
                    "text": "CryptoAnalyzer Pro - Monitoramento Alt Season"
                }
            }
            
            return await self.send_message(embeds=[embed])
            
        except Exception as e:
            logger.error(f"Error sending altseason alert to Discord: {e}")
            return {"success": False, "error": str(e)}

    async def send_test_message(self) -> Dict[str, Any]:
        """Test Discord webhook connection"""
        if not self.is_configured():
            return {"success": False, "error": "Not configured"}
        
        test_embed = {
            "title": "🧪 Test Connection",
            "description": "Discord webhook is working correctly!",
            "color": 0x00ff00,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "CryptoAnalyzer Pro - Connection Test",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/6001/6001527.png"
            }
        }
        
        result = await self.send_message(embeds=[test_embed])
        
        if result["success"]:
            logger.info("Discord webhook test successful")
        
        return result


# Global instance
discord_service = DiscordService()

