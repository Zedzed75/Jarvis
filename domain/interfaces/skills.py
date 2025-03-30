"""
Abstract skill interfaces for Jarvis

This module defines the abstract interfaces for skills
following the dependency inversion principle of clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SkillInterface(ABC):
    """Abstract interface for assistant skills"""
    
    @abstractmethod
    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        """
        Check if this skill can handle the given intent and entities
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            True if skill can handle the request, False otherwise
        """
        pass
    
    @abstractmethod
    def process(self, query: str, intent: str, entities: Dict[str, Any]) -> Optional[str]:
        """
        Process a request that this skill can handle
        
        Args:
            query: User's query text
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            Response text or None if request couldn't be handled
        """
        pass


class WeatherSkillInterface(SkillInterface):
    """Interface for weather information skill"""
    
    @abstractmethod
    def get_current_weather(self, location: Optional[str] = None) -> str:
        """
        Get current weather information
        
        Args:
            location: Location to get weather for (or default if None)
            
        Returns:
            Weather information response
        """
        pass
    
    @abstractmethod
    def get_forecast(self, location: Optional[str] = None, 
                   days: int = 1) -> str:
        """
        Get weather forecast
        
        Args:
            location: Location to get forecast for (or default if None)
            days: Number of days for forecast
            
        Returns:
            Forecast information response
        """
        pass


class TimeDateSkillInterface(SkillInterface):
    """Interface for time and date information skill"""
    
    @abstractmethod
    def get_current_time(self, timezone: Optional[str] = None) -> str:
        """
        Get current time
        
        Args:
            timezone: Timezone to get time for (or default if None)
            
        Returns:
            Current time response
        """
        pass
    
    @abstractmethod
    def get_current_date(self, timezone: Optional[str] = None) -> str:
        """
        Get current date
        
        Args:
            timezone: Timezone to get date for (or default if None)
            
        Returns:
            Current date response
        """
        pass
    
    @abstractmethod
    def get_time_between(self, start_time: str, end_time: str) -> str:
        """
        Get time duration between two times
        
        Args:
            start_time: Start time
            end_time: End time
            
        Returns:
            Duration response
        """
        pass


class PersonalitySkillInterface(SkillInterface):
    """Interface for personality responses"""
    
    @abstractmethod
    def get_greeting(self) -> str:
        """
        Get a contextual greeting
        
        Returns:
            Greeting response
        """
        pass
    
    @abstractmethod
    def get_farewell(self) -> str:
        """
        Get a farewell response
        
        Returns:
            Farewell response
        """
        pass
    
    @abstractmethod
    def get_personality_response(self, response_type: str) -> str:
        """
        Get a personality response by type
        
        Args:
            response_type: Type of personality response to get
            
        Returns:
            Personality response
        """
        pass