"""
User domain model for Jarvis

This module defines the core user entity and related value objects
for the Jarvis assistant domain.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class UserPreference:
    """Value object representing a user preference"""
    key: str
    value: Any
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __eq__(self, other):
        if not isinstance(other, UserPreference):
            return False
        return self.key == other.key and self.value == other.value
    
    def is_stale(self, max_age_days: int = 30) -> bool:
        """
        Check if preference is stale based on last update time
        
        Args:
            max_age_days: Maximum age in days before considered stale
            
        Returns:
            True if preference is stale, False otherwise
        """
        age = datetime.now() - self.last_updated
        return age.days > max_age_days


@dataclass
class Interaction:
    """Value object representing a user-assistant interaction"""
    user_input: str
    assistant_response: str
    intent: str
    entities: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def age_seconds(self) -> float:
        """Get age of interaction in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class User:
    """Entity representing a user of the assistant"""
    id: str
    name: Optional[str] = None
    preferences: List[UserPreference] = field(default_factory=list)
    interaction_history: List[Interaction] = field(default_factory=list)
    
    def add_interaction(self, interaction: Interaction) -> None:
        """
        Add an interaction to history
        
        Args:
            interaction: Interaction to add
        """
        self.interaction_history.append(interaction)
        
        # Keep history at a reasonable size
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        # Update existing preference if it exists
        for i, pref in enumerate(self.preferences):
            if pref.key == key:
                self.preferences[i] = UserPreference(key, value)
                return
        
        # Add new preference
        self.preferences.append(UserPreference(key, value))
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        for pref in self.preferences:
            if pref.key == key:
                return pref.value
        return default
    
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
        if not self.interaction_history:
            return []
        
        # Filter by time if specified
        if minutes is not None:
            max_age_seconds = minutes * 60
            filtered = [i for i in self.interaction_history 
                      if i.age_seconds <= max_age_seconds]
        else:
            filtered = self.interaction_history
        
        # Limit by count if specified
        if count is not None:
            filtered = filtered[-count:]
            
        return filtered