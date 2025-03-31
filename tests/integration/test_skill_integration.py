"""
Integration tests for skills with other components

These tests verify the integration between skills, intent recognition,
entity extraction, and other services.
"""

import unittest
import tempfile
import os
from domain.models.user import User
from application.services.conversation_service import ConversationService
from tests.mocks.mock_recognizer import MockIntentRecognizer
from tests.mocks.mock_entity_extractor import MockEntityExtractor
from tests.mocks.mock_skill import MockSkill

class TestSkillIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create user model
        self.user = User(id="test_user")
        
        # Create intent recognizer with test patterns
        self.intent_recognizer = MockIntentRecognizer({
            "weather": "weather",
            "forecast": "weather",
            "time": "time",
            "hello": "greeting"
        })
        
        # Create entity extractor with test patterns
        self.entity_extractor = MockEntityExtractor({
            "new york": {"location": "New York"},
            "tomorrow": {"date": "tomorrow"},
            "5 pm": {"time": "5 pm"}
        })
        
        # Create conversation service
        self.conversation_service = ConversationService(
            intent_recognizer=self.intent_recognizer,
            entity_extractor=self.entity_extractor,
            user=self.user
        )
        
        # Create mock skills
        self.weather_skill = MockSkill(
            name="weather",
            handled_intents=["weather"],
            responses={
                "weather": "It's sunny in New York."
            }
        )
        
        self.time_skill = MockSkill(
            name="time",
            handled_intents=["time"],
            responses={
                "time": "The current time is 3:00 PM."
            }
        )
        
        self.greeting_skill = MockSkill(
            name="greeting",
            handled_intents=["greeting"],
            responses={
                "greeting": "Hello! How can I help you today?"
            }
        )
        
        # Create skills dictionary
        self.skills = {
            "weather": self.weather_skill,
            "time": self.time_skill,
            "greeting": self.greeting_skill
        }
    
    def test_weather_skill_integration(self):
        # Process a weather query
        response = self.conversation_service.process_command(
            "What's the weather in New York?", self.skills
        )
        
        # Verify response from weather skill
        self.assertEqual(response, "It's sunny in New York.")
        
        # Verify interaction was saved
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].intent, "weather")
        self.assertEqual(self.user.interaction_history[0].entities, {"location": "New York"})
    
    def test_time_skill_integration(self):
        # Process a time query
        response = self.conversation_service.process_command(
            "What time is it?", self.skills
        )
        
        # Verify response from time skill
        self.assertEqual(response, "The current time is 3:00 PM.")
        
        # Verify interaction was saved
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].intent, "time")
    
    def test_greeting_skill_integration(self):
        # Process a greeting
        response = self.conversation_service.process_command(
            "Hello Jarvis", self.skills
        )
        
        # Verify response from greeting skill
        self.assertEqual(response, "Hello! How can I help you today?")
        
        # Verify interaction was saved
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].intent, "greeting")
    
    def test_unknown_intent_fallback(self):
        # Process an unknown query
        response = self.conversation_service.process_command(
            "Do something I don't understand", self.skills
        )
        
        # Verify fallback response
        self.assertIn(response, self.conversation_service.default_responses)
        
        # Verify interaction was saved
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].intent, "unknown")


if __name__ == '__main__':
    unittest.main()