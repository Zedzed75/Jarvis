"""
Speech processing module initialization for Jarvis

This package provides speech recognition, synthesis, and wake word detection
functionality for the Jarvis assistant.
"""

from infrastructure.speech.speech_recognizer import GoogleSpeechRecognizer, DeepSpeechRecognizer
from infrastructure.speech.text_to_speech import PollyTextToSpeech, MozillaTTS
from infrastructure.speech.wake_word_detector import PorcupineWakeDetector, SnowboyWakeDetector

__all__ = [
    'GoogleSpeechRecognizer',
    'DeepSpeechRecognizer',
    'PollyTextToSpeech',
    'MozillaTTS',
    'PorcupineWakeDetector',
    'SnowboyWakeDetector'
]