"""
Tests for the Assistant Service
"""

import unittest
from unittest.mock import Mock, patch
from application.services.assistant_service import AssistantService

class TestAssistantService(unittest.TestCase):
    
    def setUp(self):
        # Create mock config
        self.config = {
            'general': {'name': 'TestJarvis'},
            'speech': {'recognition': {}, 'synthesis': {}, 'wake_word': {}}
        }
        
        # Create mock notification service
        self.mock_notification = Mock()
        
        # Create the assistant service
        self.assistant = AssistantService(
            config=self.config,
            text_mode=True,
            notification_service=self.mock_notification
        )
        
        # Mock other dependencies
        self.assistant.speech_recognizer = Mock()
        self.assistant.text_to_speech = Mock()
        self.assistant.wake_word_detector = Mock()
        self.assistant.memory_service = Mock()
        self.assistant.conversation_service = Mock()
    
    def test_initialization(self):
        self.assertEqual(self.assistant.config, self.config)
        self.assertTrue(self.assistant.text_mode)
        self.assertEqual(self.assistant.notification_service, self.mock_notification)
        self.assertFalse(self.assistant.running)
    
    def test_set_speech_components(self):
        # Create mock components
        mock_recognizer = Mock()
        mock_synthesizer = Mock()
        mock_wake_detector = Mock()
        
        # Inject components
        self.assistant.set_speech_components(
            recognizer=mock_recognizer,
            synthesizer=mock_synthesizer,
            wake_detector=mock_wake_detector
        )
        
        # Verify components were set
        self.assertEqual(self.assistant.speech_recognizer, mock_recognizer)
        self.assertEqual(self.assistant.text_to_speech, mock_synthesizer)
        self.assertEqual(self.assistant.wake_word_detector, mock_wake_detector)
    
    def test_set_services(self):
        # Create mock services
        mock_memory = Mock()
        mock_conversation = Mock()
        
        # Inject services
        self.assistant.set_services(
            memory_service=mock_memory,
            conversation_service=mock_conversation
        )
        
        # Verify services were set
        self.assertEqual(self.assistant.memory_service, mock_memory)
        self.assertEqual(self.assistant.conversation_service, mock_conversation)
    
    def test_register_skill(self):
        # Create mock skill
        mock_skill = Mock()
        
        # Register skill
        self.assistant.register_skill('test_skill', mock_skill)
        
        # Verify skill was registered
        self.assertIn('test_skill', self.assistant.skills)
        self.assertEqual(self.assistant.skills['test_skill'], mock_skill)
    
    def test_stop(self):
        # Start the assistant
        self.assistant.running = True
        
        # Stop the assistant
        self.assistant.stop()
        
        # Verify the assistant is stopped
        self.assertFalse(self.assistant.running)
        
        # Verify notification was sent
        self.mock_notification.notify.assert_called_once()
    
    @patch('builtins.input', return_value='test command')
    def test_process_command(self, mock_input):
        # Mock conversation service response
        self.assistant.conversation_service.process_command.return_value = "Test response"
        
        # Process a command
        self.assistant._process_command("test command")
        
        # Verify conversation service was called
        self.assistant.conversation_service.process_command.assert_called_once_with(
            "test command", self.assistant.skills
        )
        
        # Verify memory service was called
        self.assistant.memory_service.save_interaction.assert_called_once()


if __name__ == '__main__':
    unittest.main()