"""
Wake Word Detection Implementation for Jarvis

This module implements the WakeWordDetectorInterface using
Picovoice Porcupine or Snowboy.
"""

import os
import struct
import logging
import time
from typing import Dict, Any, List, Optional

import pyaudio
import numpy as np

# Conditionally import Porcupine
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False

# Conditionally import Snowboy
try:
    import snowboy.snowboydetect as snowboydetect
    SNOWBOY_AVAILABLE = True
except ImportError:
    SNOWBOY_AVAILABLE = False

from domain.interfaces.repositories import WakeWordDetectorInterface

logger = logging.getLogger('jarvis.infrastructure.speech.wake_word')

class PorcupineWakeDetector(WakeWordDetectorInterface):
    """
    Picovoice Porcupine implementation of wake word detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Porcupine wake word detector
        
        Args:
            config: Configuration dictionary
        """
        if not PORCUPINE_AVAILABLE:
            raise ImportError("Picovoice Porcupine is not available. Please install pvporcupine.")
            
        self.config = config
        self.keywords = config.get('keywords', ['jarvis'])
        
        # Get access key from config
        access_key = config.get('porcupine_access_key')
        if not access_key:
            raise ValueError("Porcupine access key not provided")
            
        # Convert sensitivity to list if single value
        sensitivity = config.get('sensitivity', 0.5)
        if not isinstance(sensitivity, list):
            sensitivity = [sensitivity] * len(self.keywords)
            
        # Create porcupine instance
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=self.keywords,
            sensitivities=sensitivity
        )
        
        # Set audio parameters based on Porcupine requirements
        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length
        
        # Initialize audio interface
        self.audio = pyaudio.PyAudio()
        
        logger.info(f"Porcupine wake word detector initialized with keywords: {self.keywords}")
    
    def detect(self) -> bool:
        """
        Listen for wake word
        
        Returns:
            True if wake word detected, False otherwise
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frame_length
            )
            
            logger.debug("Listening for wake word...")
            
            # Listen until wake word is detected
            while True:
                # Read audio frame
                audio_frame = stream.read(self.frame_length, exception_on_overflow=False)
                
                # Convert audio to required format (array of int16)
                pcm = struct.unpack_from("h" * self.frame_length, audio_frame)
                
                # Process with Porcupine
                keyword_index = self.porcupine.process(pcm)
                
                # If wake word detected
                if keyword_index >= 0:
                    logger.info(f"Wake word detected: {self.keywords[keyword_index]}")
                    stream.stop_stream()
                    stream.close()
                    return True
                    
                # Small sleep to prevent CPU overuse
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error detecting wake word: {e}")
            return False
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()
            
        if hasattr(self, 'audio'):
            self.audio.terminate()


class SnowboyWakeDetector(WakeWordDetectorInterface):
    """
    Snowboy implementation of wake word detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Snowboy wake word detector
        
        Args:
            config: Configuration dictionary
        """
        if not SNOWBOY_AVAILABLE:
            raise ImportError("Snowboy is not available. Please install snowboy.")
            
        self.config = config
        
        # Get model paths
        model_paths = config.get('snowboy_model_paths')
        if not model_paths:
            raise ValueError("Snowboy model paths not provided")
            
        # Convert to list if single path
        if isinstance(model_paths, str):
            model_paths = [model_paths]
            
        # Convert sensitivity to list if single value
        sensitivity = config.get('sensitivity', 0.5)
        if not isinstance(sensitivity, list):
            sensitivity = [sensitivity] * len(model_paths)
            
        # Convert to string for Snowboy
        sensitivity_str = ",".join([str(s) for s in sensitivity])
        
        # Create detector
        resource_path = config.get('snowboy_resource_path', "resources/common.res")
        self.snowboy = snowboydetect.SnowboyDetect(
            resource_filename=resource_path,
            model_str=",".join(model_paths)
        )
        
        # Set parameters
        self.snowboy.SetSensitivity(sensitivity_str)
        self.snowboy.SetAudioGain(config.get('snowboy_audio_gain', 1.0))
        self.sample_rate = 16000  # Snowboy requires 16kHz
        self.snowboy.ApplyFrontend(config.get('snowboy_apply_frontend', False))
        
        # Set frame length
        self.frame_length = config.get('snowboy_frame_length', 512)
        
        # Initialize audio interface
        self.audio = pyaudio.PyAudio()
        
        logger.info(f"Snowboy wake word detector initialized with {len(model_paths)} models")
    
    def detect(self) -> bool:
        """
        Listen for wake word
        
        Returns:
            True if wake word detected, False otherwise
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frame_length
            )
            
            logger.debug("Listening for wake word...")
            
            # Listen until wake word is detected
            while True:
                # Read audio frame
                audio_frame = stream.read(self.frame_length, exception_on_overflow=False)
                
                # Process with Snowboy
                result = self.snowboy.RunDetection(audio_frame)
                
                # If wake word detected (result > 0)
                if result > 0:
                    logger.info(f"Wake word detected (Snowboy: {result})")
                    stream.stop_stream()
                    stream.close()
                    return True
                    
                # Small sleep to prevent CPU overuse
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error detecting wake word: {e}")
            return False
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()