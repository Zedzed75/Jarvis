"""
Domain interfaces initialization for Jarvis
"""

from domain.interfaces.repositories import (
    MemoryRepositoryInterface, 
    IntentRecognizerInterface,
    EntityExtractorInterface,
    SpeechRecognizerInterface,
    TextToSpeechInterface,
    WakeWordDetectorInterface,
    ConfigManagerInterface
)

from domain.interfaces.skills import (
    SkillInterface,
    WeatherSkillInterface,
    TimeDateSkillInterface,
    PersonalitySkillInterface
)

from domain.interfaces.notifications import (
    NotificationInterface
)

__all__ = [
    'MemoryRepositoryInterface',
    'IntentRecognizerInterface',
    'EntityExtractorInterface',
    'SpeechRecognizerInterface',
    'TextToSpeechInterface',
    'WakeWordDetectorInterface',
    'ConfigManagerInterface',
    'SkillInterface',
    'WeatherSkillInterface',
    'TimeDateSkillInterface',
    'PersonalitySkillInterface',
    'NotificationInterface'
]