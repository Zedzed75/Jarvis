"""
Integration tests for NLP components

These tests verify the integration between intent recognition, 
entity extraction, and conversation management.
"""

import unittest
from unittest.mock import Mock
from domain.models.user import User
from application.services.conversation_service import ConversationService
from tests.mocks.mock_recognizer import MockIntentRecognizer
from tests.mocks.mock_entity_extractor import MockEntityExtractor

class TestNLPIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create user model
        self.user = User(id="test_user")
        
        # Create intent recognizer with test patterns
        self.intent_recognizer = MockIntentRecognizer({
            "weather": "weather",
            "forecast": "weather",
            "temperature": "weather",
            "time": "time",
            "date": "date",
            "hello": "greeting",
            "hi": "greeting"
        })
        
        # Create entity extractor with test patterns
        self.entity_extractor = MockEntityExtractor({
            "new york": {"location": "New York"},
            "london": {"location": "London"},
            "tomorrow": {"date": "tomorrow"},
            "today": {"date": "today"},
            "5 pm": {"time": "5 pm"},
            "celsius": {"unit": "celsius"},
            "fahrenheit": {"unit": "fahrenheit"}
        })
        
        # Create conversation service
        self.conversation_service = ConversationService(
            intent_recognizer=self.intent_recognizer,
            entity_extractor=self.entity_extractor,
            user=self.user
        )
        
        # Create mock skills
        self.mock_weather_skill = Mock()
        self.mock_weather_skill.can_handle.return_value = True
        self.mock_weather_skill.process.return_value = "Weather response"
        
        self.mock_time_skill = Mock()
        self.mock_time_skill.can_handle.return_value = True
        self.mock_time_skill.process.return_value = "Time response"
        
        # Create skills dictionary
        self.skills = {
            "weather": self.mock_weather_skill,
            "time": self.mock_time_skill
        }
    
    def test_weather_intent_with_location(self):
        # Process a weather query with location
        response = self.conversation_service.process_command(
            "What's the weather in New York?", self.skills
        )
        
        # Verify the correct intent and entities were extracted
        self.mock_weather_skill.can_handle.assert_called_once_with("weather", {"location": "New York"})
        self.mock_weather_skill.process.assert_called_once_with(
            "What's the weather in New York?", "weather", {"location": "New York"}
        )
        
        # Verify the response
        self.assertEqual(response, "Weather response")
    
    def test_weather_intent_with_date(self):
        # Process a weather query with date
        response = self.conversation_service.process_command(
            "What's the weather tomorrow?", self.skills
        )
        
        # Verify the correct intent and entities were extracted
        self.mock_weather_skill.can_handle.assert_called_once_with("weather", {"date": "tomorrow"})
        self.mock_weather_skill.process.assert_called_once_with(
            "What's the weather tomorrow?", "weather", {"date": "tomorrow"}
        )
        
        # Verify the response
        self.assertEqual(response, "Weather response")
    
    def test_weather_intent_with_location_and_date(self):
        # Process a weather query with location and date
        response = self.conversation_service.process_command(
            "What's the weather tomorrow in New York?", self.skills
        )
        
        # Verify the correct intent and entities were extracted
        self.mock_weather_skill.can_handle.assert_called_once_with(
            "weather", {"location": "New York", "date": "tomorrow"}
        )
        self.mock_weather_skill.process.assert_called_once_with(
            "What's the weather tomorrow in New York?", 
            "weather", 
            {"location": "New York", "date": "tomorrow"}
        )
        
        # Verify the response
        self.assertEqual(response, "Weather response")
    
    def test_time_intent(self):
        # Process a time query
        response = self.conversation_service.process_command(
            "What time is it?", self.skills
        )
        
        # Verify the correct intent was extracted
        self.mock_time_skill.can_handle.assert_called_once_with("time", {})
        self.mock_time_skill.process.assert_called_once_with(
            "What time is it?", "time", {}
        )
        
        # Verify the response
        self.assertEqual(response, "Time response")
    
    def test_unknown_intent(self):
        # Create mock skills that can't handle the command
        mock_skill = Mock()
        mock_skill.can_handle.return_value = False
        
        skills = {"test": mock_skill}
        
        # Set a known default response for testing
        self.conversation_service.default_responses = ["I don't understand."]
        
        # Process an unknown query
        response = self.conversation_service.process_command(
            "This is an unknown command", skills
        )
        
        # Verify the fallback response was used
        self.assertEqual(response, "I don't understand.")
        
        # Verify interaction was recorded with unknown intent
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].intent, "unknown")


if __name__ == '__main__':
    unittest.main()