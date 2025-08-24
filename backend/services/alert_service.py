"""
Alert Service for CryptoAnalyzer Pro
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing alerts and notifications"""
    
    def __init__(self):
        self.alerts = []
    
    async def create_alert(self, symbol: str, condition: str, value: float, user_id: str = None) -> Dict[str, Any]:
        """Create a new alert"""
        try:
            alert = {
                "id": len(self.alerts) + 1,
                "symbol": symbol.upper(),
                "condition": condition,
                "value": value,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.alerts.append(alert)
            logger.info(f"Created alert for {symbol}: {condition} {value}")
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return {}
    
    async def get_alerts(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get all alerts for a user"""
        try:
            if user_id:
                return [alert for alert in self.alerts if alert.get("user_id") == user_id]
            return self.alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def check_alerts(self, symbol: str, current_price: float) -> List[Dict[str, Any]]:
        """Check if any alerts should be triggered"""
        triggered_alerts = []
        
        try:
            for alert in self.alerts:
                if not alert["active"] or alert["symbol"] != symbol.upper():
                    continue
                
                condition = alert["condition"]
                target_value = alert["value"]
                
                triggered = False
                
                if condition == "above" and current_price > target_value:
                    triggered = True
                elif condition == "below" and current_price < target_value:
                    triggered = True
                elif condition == "equals" and abs(current_price - target_value) < (target_value * 0.01):  # 1% tolerance
                    triggered = True
                
                if triggered:
                    alert["active"] = False
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_price"] = current_price
                    triggered_alerts.append(alert)
                    
                    logger.info(f"Alert triggered for {symbol}: {condition} {target_value} at price {current_price}")
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    async def delete_alert(self, alert_id: int, user_id: str = None) -> bool:
        """Delete an alert"""
        try:
            for i, alert in enumerate(self.alerts):
                if alert["id"] == alert_id:
                    if user_id and alert.get("user_id") != user_id:
                        return False
                    
                    del self.alerts[i]
                    logger.info(f"Deleted alert {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return False


# Global instance
alert_service = AlertService()

