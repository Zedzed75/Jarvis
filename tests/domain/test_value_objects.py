"""
Tests for domain value objects
"""

import unittest
from datetime import datetime, timedelta
from domain.models.user import UserPreference, Interaction

class TestValueObjects(unittest.TestCase):
    
    def test_user_preference_equality(self):
        pref1 = UserPreference("theme", "dark")
        pref2 = UserPreference("theme", "dark")
        pref3 = UserPreference("theme", "light")
        
        self.assertEqual(pref1, pref2)
        self.assertNotEqual(pref1, pref3)
    
    def test_user_preference_is_stale(self):
        # Create a preference with a timestamp in the past
        pref = UserPreference("theme", "dark")
        pref.last_updated = datetime.now() - timedelta(days=40)
        
        self.assertTrue(pref.is_stale(max_age_days=30))
        self.assertFalse(pref.is_stale(max_age_days=50))
    
    def test_interaction_age_seconds(self):
        # Create an interaction with a timestamp in the past
        interaction = Interaction(
            user_input="Hello",
            assistant_response="Hi there",
            intent="greeting",
            entities={}
        )
        interaction.timestamp = datetime.now() - timedelta(seconds=10)
        
        # Age should be approximately 10 seconds (allow small tolerance)
        self.assertGreaterEqual(interaction.age_seconds, 9.9)
        self.assertLessEqual(interaction.age_seconds, 11)


if __name__ == '__main__':
    unittest.main()