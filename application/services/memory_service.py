"""
Memory Service for Jarvis

This service manages short-term and long-term memory for the assistant,
following clean architecture principles.
"""

import logging
from typing import Dict, Any, List, Optional

from domain.interfaces.repositories import MemoryRepositoryInterface
from domain.models.user import User, Interaction, UserPreference

logger = logging.getLogger('jarvis.application.services.memory')

class MemoryService:
    """
    Service for managing memory and context
    """
    
    def __init__(self, memory_repository: MemoryRepositoryInterface, user: User):
        """
        Initialize the memory service
        
        Args:
            memory_repository: Component for persistent memory storage
            user: User entity for context association
        """
        self.repository = memory_repository
        self.user = user
        
        # Load previous state if available
        self._load_state()
        
        logger.info("Memory service initialized")
    
    def save_interaction(self, user_input: str, assistant_response: str, 
                        intent: str, entities: Dict[str, Any]) -> None:
        """
        Save an interaction to memory
        
        Args:
            user_input: User's input text
            assistant_response: Assistant's response
            intent: Detected intent
            entities: Extracted entities
        """
        # Create and add interaction to user's history
        interaction = Interaction(
            user_input=user_input,
            assistant_response=assistant_response,
            intent=intent,
            entities=entities
        )
        self.user.add_interaction(interaction)
        
        # Save to persistent repository
        self.repository.save_interaction(user_input, assistant_response, intent, entities)
        logger.debug("Interaction saved to memory")
    
    def get_recent_interactions(self, count: Optional[int] = None, 
                              minutes: Optional[int] = None) -> List[Interaction]:
        """
        Get recent interactions
        
        Args:
            count: Maximum number of interactions to return
            minutes: Time window in minutes
            
        Returns:
            List of recent interactions
        """
        return self.user.get_recent_interactions(count, minutes)
    
    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        # Set in user model
        self.user.set_preference(key, value)
        
        # Save to persistent repository
        self.repository.set_preference(key, value)
        logger.debug(f"Preference set: {key}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        return self.user.get_preference(key, default)
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context
        
        Returns:
            Dictionary of current context values
        """
        # Get context from repository
        return self.repository.get_context()
    
    def save_state(self) -> bool:
        """
        Save current memory state to persistent storage
        
        Returns:
            True if successful, False otherwise
        """
        return self.repository.save()
    
    def _load_state(self) -> None:
        """Load previous memory state if available"""
        if self.repository.load():
            # Sync user model with repository data
            self._sync_user_from_repository()
            logger.debug("Memory state loaded from repository")
    
    def _sync_user_from_repository(self) -> None:
        """Sync user model with data from repository"""
        # In a real implementation, this would populate the User model
        # with data from the repository, including preferences and
        # recent interactions
        
        # This is a simplified example:
        recent_interactions = self.repository.get_recent_interactions(count=10)
        
        # Clear existing interactions to avoid duplicates
        self.user.interaction_history = []
        
        # Convert repository format to domain model format
        for interaction in recent_interactions:
            self.user.add_interaction(Interaction(
                user_input=interaction.get('user_input', ''),
                assistant_response=interaction.get('assistant_response', ''),
                intent=interaction.get('intent', 'unknown'),
                entities=interaction.get('entities', {})
            ))