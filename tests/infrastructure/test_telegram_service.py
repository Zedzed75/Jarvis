"""
Tests for the Telegram Notification Service
"""

import unittest
from unittest.mock import patch, Mock
from infrastructure.notifications.telegram_service import TelegramNotificationService

class TestTelegramNotificationService(unittest.TestCase):
    
    def setUp(self):
        # Create telegram service
        self.token = "test_token"
        self.chat_id = "test_chat_id"
        self.telegram_service = TelegramNotificationService(self.token, self.chat_id)
    
    @patch('requests.post')
    def test_send_message(self, mock_post):
        # Set up mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Send message
        result = self.telegram_service.send_message("Test message", "normal")
        
        # Verify request was sent correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        # Check URL
        self.assertEqual(args[0], f"https://api.telegram.org/bot{self.token}/sendMessage")
        
        # Check data
        self.assertEqual(kwargs['data']['chat_id'], self.chat_id)
        self.assertEqual(kwargs['data']['text'], "Test message")
        
        # Check result
        self.assertTrue(result)
    
    @patch('requests.post')
    def test_send_message_with_priority(self, mock_post):
        # Set up mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Send high priority message
        self.telegram_service.send_message("Important message", "high")
        
        # Verify message was formatted correctly
        args, kwargs = mock_post.call_args
        self.assertIn("URGENT", kwargs['data']['text'])
    
    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        # Set up mock response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # Send message
        result = self.telegram_service.send_message("Test message")
        
        # Verify result
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_send_with_attachment(self, mock_post):
        # Set up mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Mock open to avoid actual file operations
        mock_file = Mock()
        with patch('builtins.open', return_value=mock_file):
            # Send message with photo
            result = self.telegram_service.send_with_attachment(
                "Photo message", "/path/to/photo.jpg", "photo"
            )
        
        # Verify request was sent correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        # Check URL
        self.assertEqual(args[0], f"https://api.telegram.org/bot{self.token}/sendPhoto")
        
        # Check data
        self.assertEqual(kwargs['data']['chat_id'], self.chat_id)
        self.assertEqual(kwargs['data']['caption'], "Photo message")
        
        # Check file
        self.assertIn('photo', kwargs['files'])
        
        # Check result
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()