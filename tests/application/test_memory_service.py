"""
Tests for the Memory Service
"""

import unittest
from unittest.mock import Mock
from application.services.memory_service import MemoryService
from domain.models.user import User

class TestMemoryService(unittest.TestCase):
    
    def setUp(self):
        # Create mock repository
        self.mock_repository = Mock()
        
        # Create user
        self.user = User(id="test_user")
        
        # Create memory service
        self.memory_service = MemoryService(self.mock_repository, self.user)
    
    def test_save_interaction(self):
        # Call save_interaction
        self.memory_service.save_interaction(
            user_input="Hello",
            assistant_response="Hi there",
            intent="greeting",
            entities={}
        )
        
        # Verify user has the interaction
        self.assertEqual(len(self.user.interaction_history), 1)
        self.assertEqual(self.user.interaction_history[0].user_input, "Hello")
        
        # Verify repository was called
        self.mock_repository.save_interaction.assert_called_once_with(
            "Hello", "Hi there", "greeting", {}
        )
    
    def test_get_recent_interactions(self):
        # Mock user's get_recent_interactions
        self.user.get_recent_interactions = Mock(return_value=["interaction1", "interaction2"])
        
        # Call get_recent_interactions
        result = self.memory_service.get_recent_interactions(count=2, minutes=10)
        
        # Verify user's method was called
        self.user.get_recent_interactions.assert_called_once_with(count=2, minutes=10)
        
        # Verify result
        self.assertEqual(result, ["interaction1", "interaction2"])
    
    def test_set_preference(self):
        # Call set_preference
        self.memory_service.set_preference("theme", "dark")
        
        # Verify user's set_preference was called
        self.assertEqual(self.user.get_preference("theme"), "dark")
        
        # Verify repository was called
        self.mock_repository.set_preference.assert_called_once_with("theme", "dark")
    
    def test_get_preference(self):
        # Mock user's get_preference
        self.user.get_preference = Mock(return_value="dark")
        
        # Call get_preference
        result = self.memory_service.get_preference("theme", "light")
        
        # Verify user's method was called
        self.user.get_preference.assert_called_once_with("theme", "light")
        
        # Verify result
        self.assertEqual(result, "dark")
    
    def test_save_state(self):
        # Call save_state
        self.memory_service.save_state()
        
        # Verify repository was called
        self.mock_repository.save.assert_called_once()


if __name__ == '__main__':
    unittest.main()