"""
Abstract repository interfaces for Jarvis

This module defines the abstract interfaces for data repositories
following the dependency inversion principle of clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class MemoryRepositoryInterface(ABC):
    """Abstract interface for memory persistence"""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        pass
    
    @abstractmethod
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        pass
    
    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context
        
        Returns:
            Dictionary of current context values
        """
        pass
    
    @abstractmethod
    def save(self) -> bool:
        """
        Save memory state to persistent storage
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self) -> bool:
        """
        Load memory state from persistent storage
        
        Returns:
            True if successful, False otherwise
        """
        pass


class IntentRecognizerInterface(ABC):
    """Abstract interface for intent recognition"""
    
    @abstractmethod
    def recognize_intent(self, text: str) -> str:
        """
        Recognize intent from text
        
        Args:
            text: User input text
            
        Returns:
            Recognized intent
        """
        pass


class EntityExtractorInterface(ABC):
    """Abstract interface for entity extraction"""
    
    @abstractmethod
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text
        
        Args:
            text: User input text
            
        Returns:
            Dictionary of extracted entities
        """
        pass


class SpeechRecognizerInterface(ABC):
    """Abstract interface for speech recognition"""
    
    @abstractmethod
    def listen(self) -> Optional[str]:
        """
        Listen for speech and convert to text
        
        Returns:
            Recognized text or None if nothing recognized
        """
        pass


class TextToSpeechInterface(ABC):
    """Abstract interface for text-to-speech"""
    
    @abstractmethod
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        pass


class WakeWordDetectorInterface(ABC):
    """Abstract interface for wake word detection"""
    
    @abstractmethod
    def detect(self) -> bool:
        """
        Listen for wake word
        
        Returns:
            True if wake word detected, False otherwise
        """
        pass


class ConfigManagerInterface(ABC):
    """Abstract interface for configuration management"""
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration
        
        Returns:
            Configuration dictionary
        """
        pass
    
    @abstractmethod
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path
        
        Args:
            key_path: Dot-separated path to the value
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        pass