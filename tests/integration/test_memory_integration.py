"""
Integration tests for memory components

These tests verify the integration between memory service, 
memory repository, and the user model.
"""

import unittest
import tempfile
import os
import json
from domain.models.user import User
from infrastructure.repositories.memory_repository import FileMemoryRepository
from application.services.memory_service import MemoryService

class TestMemoryIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_path = os.path.join(self.temp_dir.name, 'memory.json')
        
        # Create user model
        self.user = User(id="test_user", name="Test User")
        
        # Create memory repository
        self.memory_repository = FileMemoryRepository(self.memory_path)
        
        # Create memory service
        self.memory_service = MemoryService(self.memory_repository, self.user)
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_save_interaction_persistence(self):
        # Save an interaction
        self.memory_service.save_interaction(
            user_input="What's the weather?",
            assistant_response="It's sunny.",
            intent="weather",
            entities={"location": "New York"}
        )
        
        # Save to disk
        self.memory_service.save_state()
        
        # Create a new repository instance
        new_repository = FileMemoryRepository(self.memory_path)
        
        # Load from disk
        new_repository.load()
        
        # Verify interaction was loaded
        self.assertEqual(len(new_repository.interactions), 1)
        self.assertEqual(new_repository.interactions[0]['user_input'], "What's the weather?")
        self.assertEqual(new_repository.interactions[0]['assistant_response'], "It's sunny.")
        self.assertEqual(new_repository.interactions[0]['intent'], "weather")
        self.assertEqual(new_repository.interactions[0]['entities'], {"location": "New York"})
    
    def test_preference_persistence(self):
        # Set preferences
        self.memory_service.set_preference("theme", "dark")
        self.memory_service.set_preference("volume", 80)
        
        # Save to disk
        self.memory_service.save_state()
        
        # Create a new service with a new repository and user
        new_repository = FileMemoryRepository(self.memory_path)
        new_user = User(id="test_user")
        new_service = MemoryService(new_repository, new_user)
        
        # Load from disk
        new_repository.load()
        
        # Get preferences
        theme = new_repository.get_preference("theme")
        volume = new_repository.get_preference("volume")
        
        # Verify preferences were loaded
        self.assertEqual(theme, "dark")
        self.assertEqual(volume, 80)
    
    def test_user_model_sync(self):
        # Set preferences and save interactions through service
        self.memory_service.set_preference("theme", "dark")
        self.memory_service.save_interaction(
            user_input="Hello",
            assistant_response="Hi there",
            intent="greeting",
            entities={}
        )
        
        # Verify user model has been updated
        self.assertEqual(self.user.get_preference("theme"), "dark")
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].user_input, "Hello")
        
        # Create a new service with the same repository but new user
        new_user = User(id="test_user")
        new_service = MemoryService(self.memory_repository, new_user)
        
        # Call _load_state to sync from repository to user
        new_service._load_state()
        
        # Verify new user has been synced with repository data
        self.assertEqual(new_user.get_preference("theme"), "dark")
        self.assertEqual(len(new_user.interaction_history), 1)
        self.assertEqual(new_user.interaction_history[0].user_input, "Hello")


if __name__ == '__main__':
    unittest.main()