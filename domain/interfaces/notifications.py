"""
Abstract notification interfaces for Jarvis

This module defines the abstract interfaces for sending notifications
following the dependency inversion principle of clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class NotificationInterface(ABC):
    """Abstract interface for sending notifications"""
    
    @abstractmethod
    def send_message(self, message: str, priority: str = "normal") -> bool:
        """
        Send a notification message
        
        Args:
            message: Message content to send
            priority: Priority level (low, normal, high)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def send_with_attachment(self, message: str, 
                           attachment_path: str, 
                           attachment_type: str) -> bool:
        """
        Send a notification with attachment
        
        Args:
            message: Message content to send
            attachment_path: Path to attachment file
            attachment_type: Type of attachment (image, document, audio)
            
        Returns:
            True if successful, False otherwise
        """
        pass