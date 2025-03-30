"""
Memory Repository Implementation for Jarvis

Implements the MemoryRepositoryInterface to provide persistent storage
for conversation history, user preferences, and context.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from domain.interfaces.repositories import MemoryRepositoryInterface

logger = logging.getLogger('jarvis.infrastructure.repositories.memory')

class FileMemoryRepository(MemoryRepositoryInterface):
    """
    File-based implementation of the memory repository
    """
    
    def __init__(self, file_path: str, context_duration_minutes: int = 10):
        """
        Initialize the file-based memory repository
        
        Args:
            file_path: Path to the memory file
            context_duration_minutes: Duration in minutes for context expiration
        """
        self.file_path = file_path
        self.context_duration_minutes = context_duration_minutes
        
        # Initialize memory structures
        self.interactions = []
        self.preferences = {}
        self.context = {}
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        logger.info(f"File memory repository initialized with path: {file_path}")
    
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
        timestamp = time.time()
        
        # Create interaction record
        interaction = {
            'timestamp': timestamp,
            'user_input': user_input,
            'assistant_response': assistant_response,
            'intent': intent,
            'entities': entities
        }
        
        # Add to interactions list
        self.interactions.append(interaction)
        
        # Limit number of stored interactions
        max_interactions = 100
        if len(self.interactions) > max_interactions:
            self.interactions = self.interactions[-max_interactions:]
        
        # Update context based on intent and entities
        self._update_context(intent, entities)
        
        logger.debug(f"Interaction saved: {intent}")
    
    def get_recent_interactions(self, count: Optional[int] = None, 
                               minutes: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent interactions from memory
        
        Args:
            count: Maximum number of interactions to return
            minutes: Time window in minutes
            
        Returns:
            List of interaction records
        """
        if not self.interactions:
            return []
        
        # Filter by time if specified
        if minutes is not None:
            current_time = time.time()
            threshold = current_time - (minutes * 60)
            filtered = [i for i in self.interactions if i['timestamp'] >= threshold]
        else:
            filtered = self.interactions.copy()
        
        # Limit by count if specified
        if count is not None:
            filtered = filtered[-count:]
        
        return filtered
    
    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = {
            'value': value,
            'timestamp': time.time()
        }
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
        if key in self.preferences:
            return self.preferences[key]['value']
        return default
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context
        
        Returns:
            Dictionary of current context values
        """
        # Clean expired context items
        self._clean_expired_context()
        
        # Convert context to a simplified format for external use
        simplified_context = {}
        for key, item in self.context.items():
            if 'value' in item:
                simplified_context[key] = item['value']
        
        return simplified_context
    
    def save(self) -> bool:
        """
        Save memory state to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data to save
            memory_state = {
                'interactions': self.interactions,
                'preferences': self.preferences,
                'timestamp': time.time()
            }
            
            # Save to file
            with open(self.file_path, 'w') as f:
                json.dump(memory_state, f, indent=2)
            
            logger.info(f"Memory state saved to {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory state: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load memory state from file
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.file_path):
            logger.warning(f"Memory file not found: {self.file_path}")
            return False
        
        try:
            # Load from file
            with open(self.file_path, 'r') as f:
                memory_state = json.load(f)
            
            # Restore state
            self.interactions = memory_state.get('interactions', [])
            self.preferences = memory_state.get('preferences', {})
            
            logger.info(f"Memory state loaded from {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load memory state: {e}")
            return False
    
    def _update_context(self, intent: str, entities: Dict[str, Any]) -> None:
        """
        Update conversation context based on intent and entities
        
        Args:
            intent: Detected intent
            entities: Extracted entities
        """
        # Add timestamp to context for expiration
        timestamp = time.time()
        expiration = timestamp + (self.context_duration_minutes * 60)
        
        # Update context with intent
        self.context['last_intent'] = {
            'value': intent,
            'timestamp': timestamp,
            'expiration': expiration
        }
        
        # Update context with entities
        for entity_type, entity_value in entities.items():
            self.context[entity_type] = {
                'value': entity_value,
                'timestamp': timestamp,
                'expiration': expiration
            }
        
        logger.debug(f"Updated conversation context with intent: {intent}")
    
    def _clean_expired_context(self) -> None:
        """Remove expired items from conversation context"""
        current_time = time.time()
        expired_keys = []
        
        # Find expired keys
        for key, item in self.context.items():
            if 'expiration' in item and item['expiration'] < current_time:
                expired_keys.append(key)
        
        # Remove expired keys
        for key in expired_keys:
            del self.context[key]
        
        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired context items")