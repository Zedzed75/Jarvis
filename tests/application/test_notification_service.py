"""
Tests for the Notification Service
"""

import unittest
from unittest.mock import Mock
from application.services.notification_service import NotificationService

class TestNotificationService(unittest.TestCase):
    
    def setUp(self):
        # Create mock notification provider
        self.mock_provider = Mock()
        
        # Create notification service
        self.notification_service = NotificationService(self.mock_provider)
    
    def test_notify(self):
        # Call notify
        self.notification_service.notify("Test message", "normal")
        
        # Verify provider's send_message was called
        self.mock_provider.send_message.assert_called_once_with("Test message", "normal")
    
    def test_notify_with_image(self):
        # Call notify_with_image
        self.notification_service.notify_with_image("Test message", "/path/to/image.jpg")
        
        # Verify provider's send_with_attachment was called correctly
        self.mock_provider.send_with_attachment.assert_called_once_with(
            "Test message", "/path/to/image.jpg", "photo"
        )
    
    def test_notify_with_document(self):
        # Call notify_with_document
        self.notification_service.notify_with_document("Test message", "/path/to/doc.pdf")
        
        # Verify provider's send_with_attachment was called correctly
        self.mock_provider.send_with_attachment.assert_called_once_with(
            "Test message", "/path/to/doc.pdf", "document"
        )
    
    def test_notify_with_audio(self):
        # Call notify_with_audio
        self.notification_service.notify_with_audio("Test message", "/path/to/audio.mp3")
        
        # Verify provider's send_with_attachment was called correctly
        self.mock_provider.send_with_attachment.assert_called_once_with(
            "Test message", "/path/to/audio.mp3", "audio"
        )
    
    def test_notify_with_video(self):
        # Call notify_with_video
        self.notification_service.notify_with_video("Test message", "/path/to/video.mp4")
        
        # Verify provider's send_with_attachment was called correctly
        self.mock_provider.send_with_attachment.assert_called_once_with(
            "Test message", "/path/to/video.mp4", "video"
        )


if __name__ == '__main__':
    unittest.main()