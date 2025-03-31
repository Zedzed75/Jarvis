"""
Tests for the Memory Repository
"""

import os
import json
import unittest
import tempfile
import time
from infrastructure.repositories.memory_repository import FileMemoryRepository

class TestFileMemoryRepository(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test memory file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_path = os.path.join(self.temp_dir.name, 'memory.json')
        
        # Create memory repository
        self.repository = FileMemoryRepository(self.memory_path, context_duration_minutes=10)
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_save_interaction(self):
        # Save an interaction
        self.repository.save_interaction(
            user_input="Hello",
            assistant_response="Hi there",
            intent="greeting",
            entities={}
        )
        
        # Verify interaction was saved
        self.assertEqual(len(self.repository.interactions), 1)
        self.assertEqual(self.repository.interactions[0]['user_input'], "Hello")
        self.assertEqual(self.repository.interactions[0]['assistant_response'], "Hi there")
        self.assertEqual(self.repository.interactions[0]['intent'], "greeting")
    
    def test_get_recent_interactions(self):
        # Save multiple interactions
        for i in range(5):
            self.repository.save_interaction(
                user_input=f"Input {i}",
                assistant_response=f"Response {i}",
                intent="test",
                entities={}
            )
        
        # Get the 3 most recent interactions
        recent = self.repository.get_recent_interactions(count=3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1]['user_input'], "Input 4")
    
    def test_set_and_get_preference(self):
        # Set a preference
        self.repository.set_preference("theme", "dark")
        
        # Verify preference was set
        self.assertIn("theme", self.repository.preferences)
        self.assertEqual(self.repository.preferences["theme"]["value"], "dark")
        
        # Get the preference
        value = self.repository.get_preference("theme")
        self.assertEqual(value, "dark")
        
        # Get non-existent preference with default
        value = self.repository.get_preference("non_existent", "default")
        self.assertEqual(value, "default")
    
    def test_update_context(self):
        # Update context
        self.repository._update_context("weather", {"location": "New York"})
        
        # Verify context was updated
        self.assertIn("last_intent", self.repository.context)
        self.assertEqual(self.repository.context["last_intent"]["value"], "weather")
        
        self.assertIn("location", self.repository.context)
        self.assertEqual(self.repository.context["location"]["value"], "New York")
    
    def test_get_context(self):
        # Update context
        self.repository._update_context("weather", {"location": "New York"})
        
        # Get context
        context = self.repository.get_context()
        
        # Verify simplified context
        self.assertEqual(context["last_intent"], "weather")
        self.assertEqual(context["location"], "New York")
    
    def test_clean_expired_context(self):
        # Add context item with short expiration
        self.repository.context["test_key"] = {
            "value": "test_value",
            "timestamp": time.time(),
            "expiration": time.time() - 1  # Already expired
        }
        
        # Clean expired context
        self.repository._clean_expired_context()
        
        # Verify item was removed
        self.assertNotIn("test_key", self.repository.context)
    
    def test_save_and_load(self):
        # Save interactions and preferences
        self.repository.save_interaction(
            user_input="Hello",
            assistant_response="Hi there",
            intent="greeting",
            entities={}
        )
        
        self.repository.set_preference("theme", "dark")
        
        # Save to file
        self.repository.save()
        
        # Create new repository instance to load from file
        new_repository = FileMemoryRepository(self.memory_path)
        new_repository.load()
        
        # Verify data was loaded correctly
        self.assertEqual(len(new_repository.interactions), 1)
        self.assertEqual(new_repository.interactions[0]['user_input'], "Hello")
        
        self.assertIn("theme", new_repository.preferences)
        self.assertEqual(new_repository.preferences["theme"]["value"], "dark")


if __name__ == '__main__':
    unittest.main()