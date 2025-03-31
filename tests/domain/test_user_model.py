"""
Tests for the User domain model
"""

import unittest
from datetime import datetime, timedelta
from domain.models.user import User, Interaction, UserPreference

class TestUserModel(unittest.TestCase):
    
    def setUp(self):
        self.user = User(id="test_user", name="Test User")
    
    def test_user_creation(self):
        self.assertEqual(self.user.id, "test_user")
        self.assertEqual(self.user.name, "Test User")
        self.assertEqual(len(self.user.preferences), 0)
        self.assertEqual(len(self.user.interaction_history), 0)
    
    def test_set_preference(self):
        self.user.set_preference("theme", "dark")
        self.assertEqual(self.user.get_preference("theme"), "dark")
        
        # Test overwriting existing preference
        self.user.set_preference("theme", "light")
        self.assertEqual(self.user.get_preference("theme"), "light")
    
    def test_get_preference_with_default(self):
        # Test non-existent preference with default
        self.assertEqual(self.user.get_preference("non_existent", "default_value"), "default_value")
    
    def test_add_interaction(self):
        interaction = Interaction(
            user_input="What's the weather?",
            assistant_response="It's sunny.",
            intent="weather",
            entities={"location": "New York"}
        )
        self.user.add_interaction(interaction)
        
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].user_input, "What's the weather?")
    
    def test_get_recent_interactions_by_count(self):
        # Add multiple interactions
        for i in range(5):
            interaction = Interaction(
                user_input=f"Input {i}",
                assistant_response=f"Response {i}",
                intent="test",
                entities={}
            )
            self.user.add_interaction(interaction)
        
        # Get the 3 most recent interactions
        recent = self.user.get_recent_interactions(count=3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1].user_input, "Input 4")
    
    def test_get_recent_interactions_by_time(self):
        # Add an older interaction (manually set timestamp)
        old_interaction = Interaction(
            user_input="Old input",
            assistant_response="Old response",
            intent="test",
            entities={}
        )
        old_interaction.timestamp = datetime.now() - timedelta(minutes=30)
        self.user.add_interaction(old_interaction)
        
        # Add a recent interaction
        recent_interaction = Interaction(
            user_input="Recent input",
            assistant_response="Recent response",
            intent="test",
            entities={}
        )
        self.user.add_interaction(recent_interaction)
        
        # Get interactions from the last 10 minutes
        recent = self.user.get_recent_interactions(minutes=10)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].user_input, "Recent input")


if __name__ == '__main__':
    unittest.main()