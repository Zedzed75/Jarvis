"""
Telegram notification service for Jarvis

This module implements the notification interface using Telegram Bot API
to send messages and attachments to a specified chat.
"""

import logging
import requests
from typing import Optional, Dict, Any
from domain.interfaces.notifications import NotificationInterface

logger = logging.getLogger('jarvis.infrastructure.notifications.telegram')

class TelegramNotificationService(NotificationInterface):
    """Implements notification service using Telegram"""
    
    def __init__(self, token: str, chat_id: str):
        """
        Initialize Telegram notification service
        
        Args:
            token: Telegram Bot API token
            chat_id: Telegram chat ID to send messages to
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        logger.info("Telegram notification service initialized")
    
    def send_message(self, message: str, priority: str = "normal") -> bool:
        """
        Send a text message via Telegram
        
        Args:
            message: Message to send
            priority: Priority level (affects formatting)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Format message based on priority
            if priority == "high":
                message = f"🚨 *URGENT* 🚨\n{message}"
            elif priority == "low":
                message = f"ℹ️ {message}"
                
            # Send message
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(f"{self.base_url}/sendMessage", data=data)
            
            if response.status_code == 200:
                logger.debug(f"Telegram message sent: {message[:50]}...")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_with_attachment(self, message: str, 
                           attachment_path: str, 
                           attachment_type: str = "photo") -> bool:
        """
        Send a message with attachment via Telegram
        
        Args:
            message: Message to send
            attachment_path: Path to attachment file
            attachment_type: Type of attachment (photo, document, audio, video)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine the correct API method based on attachment type
            method = f"send{attachment_type.capitalize()}"
            url = f"{self.base_url}/{method}"
            
            # Prepare files and data
            files = {}
            data = {
                'chat_id': self.chat_id,
                'caption': message
            }
            
            # Configure the appropriate parameter based on type
            param_name = attachment_type
            if attachment_type == "photo":
                files = {param_name: open(attachment_path, 'rb')}
            elif attachment_type == "document":
                files = {param_name: open(attachment_path, 'rb')}
            elif attachment_type in ["audio", "video"]:
                files = {param_name: open(attachment_path, 'rb')}
            else:
                logger.error(f"Unsupported attachment type: {attachment_type}")
                return False
            
            # Send message with attachment
            response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                logger.debug(f"Telegram message with {attachment_type} sent")
                return True
            else:
                logger.error(f"Failed to send Telegram message with attachment: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message with attachment: {e}")
            return False
        finally:
            # Close file handles if they were opened
            for file_obj in files.values():
                if hasattr(file_obj, 'close'):
                    file_obj.close()