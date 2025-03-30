"""
Notification factory for creating notification services based on configuration.
"""

import logging
from typing import Dict, Any, Optional
from domain.interfaces.notifications import NotificationInterface
from infrastructure.notifications.telegram_service import TelegramNotificationService

logger = logging.getLogger('jarvis.infrastructure.notifications.factory')

def create_notification_service(config: Dict[str, Any]) -> Optional[NotificationInterface]:
    """
    Create a notification service based on configuration
    
    Args:
        config: Configuration dictionary with notification settings
        
    Returns:
        Notification service instance or None if configuration is invalid
    """
    if not config or 'provider' not in config or not config.get('enabled', True):
        logger.warning("Notifications not configured or disabled")
        return None
        
    provider = config['provider']
    
    if provider == 'telegram':
        return _create_telegram_service(config.get('telegram', {}))
    # Add other notification providers here as needed
    else:
        logger.error(f"Unsupported notification provider: {provider}")
        return None
        
def _create_telegram_service(config: Dict[str, Any]) -> Optional[TelegramNotificationService]:
    """
    Create a Telegram notification service
    
    Args:
        config: Telegram-specific configuration
        
    Returns:
        TelegramNotificationService instance or None if configuration is invalid
    """
    token = config.get('token')
    chat_id = config.get('chat_id')
    
    if not token or not chat_id:
        logger.error("Telegram configuration missing token or chat_id")
        return None
        
    logger.info("Creating Telegram notification service")
    return TelegramNotificationService(token, chat_id)