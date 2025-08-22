"""
Alert System Service - FIXED VERSION
Resolves ImportError and provides functional alert management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# ALERT_CONFIG defined locally to fix ImportError
ALERT_CONFIG = {
    "max_alerts_per_user": 100,
    "cooldown_minutes": 5,
    "priority_levels": ["low", "medium", "high", "critical"],
    "alert_types": ["price", "volume", "technical", "news"],
    "notification_channels": ["email", "telegram", "discord", "webhook"]
}


class AlertService:
    """Alert management service"""
    
    def __init__(self):
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
        self.cooldown_tracker: Dict[str, datetime] = {}
        
    async def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
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
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def check_alerts(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check alerts against market data"""
        triggered_alerts = []
        
        try:
            for alert_id, alert in self.active_alerts.items():
                if not alert["is_active"] or alert["is_triggered"]:
                    continue
                
                symbol = alert["symbol"]
                if symbol not in market_data:
                    continue
                
                current_price = market_data[symbol].get("price", 0)
                alert["current_value"] = current_price
                
                # Check if alert condition is met
                if self._check_condition(alert, current_price):
                    # Check cooldown
                    if self._is_in_cooldown(alert_id):
                        continue
                    
                    # Trigger alert
                    alert["is_triggered"] = True
                    alert["triggered_at"] = datetime.now().isoformat()
                    
                    triggered_alerts.append(alert)
                    self.cooldown_tracker[alert_id] = datetime.now()
                    
                    logger.info(f"Alert triggered: {alert_id} for {symbol}")
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    def _check_condition(self, alert: Dict[str, Any], current_value: float) -> bool:
        """Check if alert condition is met"""
        try:
            condition = alert["condition"]
            target_value = alert["target_value"]
            
            if condition == "above":
                return current_value > target_value
            elif condition == "below":
                return current_value < target_value
            elif condition == "crosses_above":
                # Simple implementation - would need historical data for proper crossing detection
                return current_value > target_value
            elif condition == "crosses_below":
                return current_value < target_value
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking condition: {e}")
            return False
    
    def _is_in_cooldown(self, alert_id: str) -> bool:
        """Check if alert is in cooldown period"""
        if alert_id not in self.cooldown_tracker:
            return False
        
        cooldown_time = self.cooldown_tracker[alert_id]
        cooldown_minutes = ALERT_CONFIG["cooldown_minutes"]
        
        return datetime.now() < cooldown_time + timedelta(minutes=cooldown_minutes)
    
    async def get_alerts(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Get alerts for a user"""
        try:
            user_alerts = [
                alert for alert in self.active_alerts.values()
                if alert["user_id"] == user_id
            ]
            return user_alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def update_alert(self, alert_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing alert"""
        try:
            if alert_id not in self.active_alerts:
                return None
            
            alert = self.active_alerts[alert_id]
            
            # Update allowed fields
            allowed_fields = ["target_value", "condition", "is_active", "priority", "message"]
            for field in allowed_fields:
                if field in update_data:
                    alert[field] = update_data[field]
            
            logger.info(f"Alert updated: {alert_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Error updating alert: {e}")
            return None
    
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
    
    async def send_notification(self, alert: Dict[str, Any]) -> bool:
        """Send notification for triggered alert"""
        try:
            # Mock notification sending
            logger.info(f"📢 ALERT: {alert['symbol']} - {alert['message']}")
            
            # In real implementation, would send via:
            # - Email
            # - Telegram
            # - Discord
            # - Webhook
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        try:
            total_alerts = len(self.active_alerts)
            active_alerts = len([a for a in self.active_alerts.values() if a["is_active"]])
            triggered_alerts = len([a for a in self.active_alerts.values() if a["is_triggered"]])
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "triggered_alerts": triggered_alerts,
                "alert_types": ALERT_CONFIG["alert_types"],
                "priority_levels": ALERT_CONFIG["priority_levels"]
            }
            
        except Exception as e:
            logger.error(f"Error getting alert stats: {e}")
            return {}


# Global alert service instance
alert_service = AlertService()

