import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = None  # Será obtido automaticamente
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        
    async def get_telegram_chat_id(self):
        """Obter chat_id automaticamente"""
        if not self.telegram_token:
            return None
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['result']:
                            # Pegar o chat_id da última mensagem
                            self.telegram_chat_id = data['result'][-1]['message']['chat']['id']
                            return self.telegram_chat_id
        except Exception as e:
            logger.error(f"Erro ao obter chat_id: {e}")
        
        return None
    
    async def send_telegram_message(self, message: str, parse_mode: str = 'HTML'):
        """Enviar mensagem para Telegram"""
        if not self.telegram_token:
            logger.warning("Telegram token não configurado")
            return False
            
        if not self.telegram_chat_id:
            await self.get_telegram_chat_id()
            
        if not self.telegram_chat_id:
            logger.warning("Chat ID não encontrado. Envie uma mensagem para o bot primeiro.")
            return False
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("✅ Mensagem Telegram enviada com sucesso")
                        return True
                    else:
                        logger.error(f"❌ Erro Telegram: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar Telegram: {e}")
            return False
    
    async def send_discord_message(self, message: str, color: int = 0x00ff00):
        """Enviar mensagem para Discord"""
        if not self.discord_webhook:
            logger.warning("Discord webhook não configurado")
            return False
            
        embed = {
            "title": "🚀 CryptoAnalyzer Pro",
            "description": message,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "CryptoAnalyzer Pro Bot"
            }
        }
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook, json=payload) as response:
                    if response.status in [200, 204]:
                        logger.info("✅ Mensagem Discord enviada com sucesso")
                        return True
                    else:
                        logger.error(f"❌ Erro Discord: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar Discord: {e}")
            return False
    
    async def notify_system_start(self):
        """Notificar início do sistema"""
        message = f"""
🚀 <b>CryptoAnalyzer Pro INICIADO!</b>

✅ Backend: Online
✅ Análise Técnica: Ativa  
✅ Coleta de Dados: Funcionando
✅ Alt Season Monitor: Ligado
✅ Notificações: Configuradas

🕐 <i>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>
        """
        
        await self._send_to_all(message, "success")
    
    async def notify_system_stop(self):
        """Notificar parada do sistema"""
        message = f"""
⏹️ <b>CryptoAnalyzer Pro PARADO</b>

📊 Coleta de dados interrompida
🔍 Análise técnica pausada
🚨 Alertas desativados

🕐 <i>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>
        """
        
        await self._send_to_all(message, "warning")
    
    async def notify_analysis_complete(self, analysis_data: Dict[str, Any]):
        """Notificar análise concluída"""
        top_coins = analysis_data.get('top_recommendations', [])
        btc_dominance = analysis_data.get('btc_dominance', 0)
        
        message = f"""
📊 <b>Análise Técnica Concluída!</b>

🏆 <b>Top 5 Altcoins:</b>
"""
        
        for i, coin in enumerate(top_coins[:5], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            message += f"{emoji} {coin.get('symbol', 'N/A')} - Score: {coin.get('score', 0)}\n"
        
        message += f"""
📈 <b>Dominância BTC:</b> {btc_dominance:.1f}%
🔍 <b>Status Alt Season:</b> {'🟢 ATIVO' if btc_dominance < 58 else '🟡 Aguardando'}

🕐 <i>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>
        """
        
        await self._send_to_all(message, "success")
    
    async def notify_alert(self, alert_type: str, coin: str, message_text: str):
        """Notificar alerta específico"""
        message = f"""
🚨 <b>Alerta: {alert_type}</b>

💰 <b>{coin}</b>

{message_text}

🕐 <i>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>
        """
        
        await self._send_to_all(message, "warning")
    
    async def _send_to_all(self, message: str, notification_type: str = "info"):
        """Enviar para todos os canais configurados"""
        colors = {
            "success": 0x00ff00,  # Verde
            "warning": 0xffaa00,  # Laranja  
            "error": 0xff0000,    # Vermelho
            "info": 0x0099ff      # Azul
        }
        
        color = colors.get(notification_type, 0x0099ff)
        
        tasks = []
        if self.telegram_token:
            tasks.append(self.send_telegram_message(message))
        
        if self.discord_webhook:
            tasks.append(self.send_discord_message(message, color))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return any(result is True for result in results)
        
        return False

# Instância global
notification_service = NotificationService()

