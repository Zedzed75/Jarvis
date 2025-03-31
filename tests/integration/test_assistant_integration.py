"""
Integration tests for the Jarvis assistant

These tests check the integration between multiple components.
"""

import unittest
import tempfile
import os
from domain.models.user import User
from infrastructure.config.config_manager import ConfigManager
from infrastructure.repositories.memory_repository import FileMemoryRepository
from application.services.memory_service import MemoryService
from application.services.conversation_service import ConversationService
from application.services.assistant_service import AssistantService

class TestAssistantIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create test user
        self.user = User(id="test_user")
        
        # Create memory repository
        memory_path = os.path.join(self.temp_dir.name, 'memory.json')
        self.memory_repository = FileMemoryRepository(memory_path)
        
        # Create memory service
        self.memory_service = MemoryService(self.memory_repository, self.user)
        
        # Create mock objects for other dependencies
        self.mock_intent_recognizer = unittest.mock.Mock()
        self.mock_entity_extractor = unittest.mock.Mock()
        self.mock_notification_service = unittest.mock.Mock()
        
        # Set up mock behavior
        self.mock_intent_recognizer.recognize_intent.return_value = "greeting"
        self.mock_entity_extractor.extract_entities.return_value = {}
        
        # Create conversation service
        self.conversation_service = ConversationService(
            intent_recognizer=self.mock_intent_recognizer,
            entity_extractor=self.mock_entity_extractor,
            user=self.user
        )
        
        # Create test config
        self.config = {
            'general': {
                'name': 'TestJarvis'
            }
        }
        
        # Create assistant service
        self.assistant = AssistantService(
            config=self.config,
            text_mode=True,
            notification_service=self.mock_notification_service
        )
        
        # Set services
        self.assistant.set_services(
            memory_service=self.memory_service,
            conversation_service=self.conversation_service
        )
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_process_command_end_to_end(self):
        # Create a mock skill
        mock_skill = unittest.mock.Mock()
        mock_skill.can_handle.return_value = True
        mock_skill.process.return_value = "Hello to you too!"
        
        # Register skill
        self.assistant.register_skill('greeting', mock_skill)
        
        # Process a command
        self.assistant._process_command("Hello Jarvis")
        
        # Verify intent recognition was called
        self.mock_intent_recognizer.recognize_intent.assert_called_once_with("Hello Jarvis")
        
        # Verify entity extraction was called
        self.mock_entity_extractor.extract_entities.assert_called_once_with("Hello Jarvis")
        
        # Verify skill was called
        mock_skill.can_handle.assert_called_once_with("greeting", {})
        mock_skill.process.assert_called_once_with("Hello Jarvis", "greeting", {})
        
        # Verify interaction was saved
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].user_input, "Hello Jarvis")
        self.assertEqual(self.user.interaction_history[0].assistant_response, "Hello to you too!")
        
        # Verify repository has the interaction
        self.assertEqual(len(self.memory_repository.interactions), 1)
        self.assertEqual(self.memory_repository.interactions[0]['user_input'], "Hello Jarvis")
    
    def test_skill_fallback(self):
        # Create a mock skill that can't handle the intent
        mock_skill = unittest.mock.Mock()
        mock_skill.can_handle.return_value = False
        
        # Register skill
        self.assistant.register_skill('greeting', mock_skill)
        
        # Set up conversation service to return a default response
        self.conversation_service._get_default_response = unittest.mock.Mock(
            return_value="I'm not sure how to help with that."
        )
        
        # Proc