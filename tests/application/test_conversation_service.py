"""
Tests for the Conversation Service
"""

import unittest
from unittest.mock import Mock
from application.services.conversation_service import ConversationService
from domain.models.user import User, Interaction

class TestConversationService(unittest.TestCase):
    
    def setUp(self):
        # Create mock components
        self.mock_intent_recognizer = Mock()
        self.mock_entity_extractor = Mock()
        
        # Create user
        self.user = User(id="test_user")
        
        # Create conversation service
        self.conversation_service = ConversationService(
            intent_recognizer=self.mock_intent_recognizer,
            entity_extractor=self.mock_entity_extractor,
            user=self.user
        )
        
        # Set up mocks
        self.mock_intent_recognizer.recognize_intent.return_value = "weather"
        self.mock_entity_extractor.extract_entities.return_value = {"location": "New York"}
    
    def test_process_command_with_skill(self):
        # Create mock skill
        mock_skill = Mock()
        mock_skill.can_handle.return_value = True
        mock_skill.process.return_value = "It's sunny in New York."
        
        # Create skills dictionary
        skills = {"weather": mock_skill}
        
        # Process command
        response = self.conversation_service.process_command("What's the weather in New York?", skills)
        
        # Verify intent and entities were extracted
        self.mock_intent_recognizer.recognize_intent.assert_called_once_with(
            "What's the weather in New York?"
        )
        
        self.mock_entity_extractor.extract_entities.assert_called_once_with(
            "What's the weather in New York?"
        )
        
        # Verify skill was called
        mock_skill.can_handle.assert_called_once_with("weather", {"location": "New York"})
        mock_skill.process.assert_called_once_with(
            "What's the weather in New York?", "weather", {"location": "New York"}
        )
        
        # Verify response
        self.assertEqual(response, "It's sunny in New York.")
        
        # Verify interaction was added to user
        self.assertEqual(len(self.user.interaction_history), 1)
    
    def test_process_command_with_fallback(self):
        # Create mock skill that can't handle the request
        mock_skill = Mock()
        mock_skill.can_handle.return_value = False
        
        # Create skills dictionary
        skills = {"weather": mock_skill}
        
        # Override default responses for deterministic testing
        self.conversation_service.default_responses = ["I don't understand."]
        
        # Process command
        response = self.conversation_service.process_command("What's the meaning of life?", skills)
        
        # Verify skill was called but couldn't handle
        mock_skill.can_handle.assert_called_once_with("weather", {"location": "New York"})
        mock_skill.process.assert_not_called()
        
        # Verify default response was used
        self.assertEqual(response, "I don't understand.")
        
        # Verify interaction was added to user
        self.assertEqual(len(self.user.interaction_history), 1)


if __name__ == '__main__':
    unittest.main()