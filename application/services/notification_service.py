"""
Notification service for Jarvis

This service coordinates notification operations using the dependency
injection principle to maintain clean architecture.
"""

import logging
from typing import Dict, Any, Optional
from domain.interfaces.notifications import NotificationInterface

logger = logging.getLogger('jarvis.application.services.notification')

class NotificationService:
    """Service for handling notifications across the application"""
    
    def __init__(self, notification_provider: NotificationInterface):
        """
        Initialize notification service
        
        Args:
            notification_provider: Implementation of notification interface
        """
        self.provider = notification_provider
        logger.info("Notification service initialized")
    
    def notify(self, message: str, priority: str = "normal") -> bool:
        """
        Send a notification
        
        Args:
            message: Message to send
            priority: Priority level
            
        Returns:
            True if successful, False otherwise
        """
        return self.provider.send_message(message, priority)
    
    def notify_with_image(self, message: str, image_path: str) -> bool:
        """
        Send a notification with image
        
        Args:
            message: Message to send
            image_path: Path to image file
            
        Returns:
            True if successful, False otherwise
        """
        return self.provider.send_with_attachment(message, image_path, "photo")
    
    def notify_with_document(self, message: str, doc_path: str) -> bool:
        """
        Send a notification with document
        
        Args:
            message: Message to send
            doc_path: Path to document file
            
        Returns:
            True if successful, False otherwise
        """
        return self.provider.send_with_attachment(message, doc_path, "document")
    
    def notify_with_audio(self, message: str, audio_path: str) -> bool:
        """
        Send a notification with audio
        
        Args:
            message: Message to send
            audio_path: Path to audio file
            
        Returns:
            True if successful, False otherwise
        """
        return self.provider.send_with_attachment(message, audio_path, "audio")
    
    def notify_with_video(self, message: str, video_path: str) -> bool:
        """
        Send a notification with video
        
        Args:
            message: Message to send
            video_path: Path to video file
            
        Returns:
            True if successful, False otherwise
        """
        return self.provider.send_with_attachment(message, video_path, "video")