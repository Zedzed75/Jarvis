"""
Speech Recognition Implementation for Jarvis

This module implements the SpeechRecognizerInterface using
Google Cloud Speech-to-Text or Mozilla DeepSpeech.
"""

import os
import io
import wave
import logging
import tempfile
import struct
import numpy as np
from typing import Dict, Any, Optional

import pyaudio

# Conditionally import Google Cloud Speech
try:
    from google.cloud import speech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Conditionally import DeepSpeech
try:
    import deepspeech
    DEEPSPEECH_AVAILABLE = True
except ImportError:
    DEEPSPEECH_AVAILABLE = False

from domain.interfaces.repositories import SpeechRecognizerInterface

logger = logging.getLogger('jarvis.infrastructure.speech.recognition')

class GoogleSpeechRecognizer(SpeechRecognizerInterface):
    """
    Google Cloud Speech-to-Text implementation
    """
    
    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Google Cloud Speech recognizer
        
        Args:
            config: Configuration dictionary
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Cloud Speech is not available. Please install google-cloud-speech.")
            
        self.config = config
        self.language = config.get('language', 'en-US')
        self.timeout = config.get('timeout_seconds', 5)
        self.audio = pyaudio.PyAudio()
        
        # Check if credentials file path is provided
        credentials_file = config.get('google_credentials_file')
        if credentials_file:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            
        # Initialize the client
        self.client = speech.SpeechClient()
        self.recognition_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.RATE,
            language_code=self.language,
            model=config.get('google_model', 'command_and_search'),
            enable_automatic_punctuation=True
        )
        
        logger.info("Google Cloud Speech recognizer initialized")
    
    def listen(self) -> Optional[str]:
        """
        Listen for speech and convert to text
        
        Returns:
            Recognized text or None if nothing recognized
        """
        audio_data = self._record_audio()
        if not audio_data:
            return None
            
        return self._recognize(audio_data)
    
    def _record_audio(self) -> Optional[bytes]:
        """
        Record audio from microphone
        
        Returns:
            Recorded audio data as bytes
        """
        logger.debug("Starting audio recording")
        
        # Open stream
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Record audio in chunks and detect silence
        frames = []
        silent_chunks = 0
        energy_threshold = self.config.get('energy_threshold', 300)
        silent_chunks_threshold = self.config.get('silent_chunks_threshold', 10)
        
        # Record for a specific duration or until silence
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Check if this chunk is silent
            energy = self._calculate_energy(data)
            if energy < energy_threshold:
                silent_chunks += 1
                if silent_chunks >= silent_chunks_threshold:
                    logger.debug("Detected silence, stopping recording")
                    break
            else:
                silent_chunks = 0
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        
        # Combine all recorded frames
        audio_data = b''.join(frames)
        
        # Check if we captured anything meaningful
        if len(frames) < 3:  # Too short to be meaningful speech
            logger.debug("Recorded audio too short, ignoring")
            return None
            
        logger.debug(f"Audio recording complete, {len(frames)} chunks captured")
        return audio_data
    
    def _calculate_energy(self, data: bytes) -> float:
        """
        Calculate the energy level of an audio chunk
        
        Args:
            data: Audio data chunk
            
        Returns:
            Energy level
        """
        # Convert bytes to int16 values for energy calculation
        count = len(data) // 2
        format_str = f"{count}h"
        shorts = struct.unpack(format_str, data)
        
        # Calculate RMS as energy
        sum_squares = sum(s * s for s in shorts)
        return (sum_squares / count) ** 0.5 if count > 0 else 0
    
    def _recognize(self, audio_data: bytes) -> Optional[str]:
        """
        Recognize speech using Google Cloud Speech
        
        Args:
            audio_data: Recorded audio data
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            audio = speech.RecognitionAudio(content=audio_data)
            response = self.client.recognize(
                config=self.recognition_config,
                audio=audio
            )
            
            if not response.results:
                logger.debug("No speech recognized")
                return None
                
            # Get the top result
            result = response.results[0].alternatives[0].transcript
            confidence = response.results[0].alternatives[0].confidence
            
            logger.debug(f"Google recognized: '{result}' with confidence: {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Google speech recognition error: {e}")
            return None
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()


class DeepSpeechRecognizer(SpeechRecognizerInterface):
    """
    Mozilla DeepSpeech implementation
    """
    
    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DeepSpeech recognizer
        
        Args:
            config: Configuration dictionary
        """
        if not DEEPSPEECH_AVAILABLE:
            raise ImportError("Mozilla DeepSpeech is not available. Please install deepspeech.")
            
        self.config = config
        self.timeout = config.get('timeout_seconds', 5)
        self.audio = pyaudio.PyAudio()
        
        # Load DeepSpeech model
        model_path = config.get('deepspeech_model_path')
        if not model_path:
            raise ValueError("DeepSpeech model path not provided")
            
        self.model = deepspeech.Model(model_path)
        
        # Load scorer if provided
        scorer_path = config.get('deepspeech_scorer_path')
        if scorer_path:
            self.model.enableExternalScorer(scorer_path)
        
        logger.info("DeepSpeech recognizer initialized")
    
    def listen(self) -> Optional[str]:
        """
        Listen for speech and convert to text
        
        Returns:
            Recognized text or None if nothing recognized
        """
        audio_data = self._record_audio()
        if not audio_data:
            return None
            
        return self._recognize(audio_data)
    
    def _record_audio(self) -> Optional[bytes]:
        """
        Record audio from microphone
        
        Returns:
            Recorded audio data as bytes
        """
        logger.debug("Starting audio recording")
        
        # Open stream
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Record audio in chunks and detect silence
        frames = []
        silent_chunks = 0
        energy_threshold = self.config.get('energy_threshold', 300)
        silent_chunks_threshold = self.config.get('silent_chunks_threshold', 10)
        
        # Record for a specific duration or until silence
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Check if this chunk is silent
            energy = self._calculate_energy(data)
            if energy < energy_threshold:
                silent_chunks += 1
                if silent_chunks >= silent_chunks_threshold:
                    logger.debug("Detected silence, stopping recording")
                    break
            else:
                silent_chunks = 0
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        
        # Combine all recorded frames
        audio_data = b''.join(frames)
        
        # Check if we captured anything meaningful
        if len(frames) < 3:  # Too short to be meaningful speech
            logger.debug("Recorded audio too short, ignoring")
            return None
            
        logger.debug(f"Audio recording complete, {len(frames)} chunks captured")
        return audio_data
    
    def _calculate_energy(self, data: bytes) -> float:
        """
        Calculate the energy level of an audio chunk
        
        Args:
            data: Audio data chunk
            
        Returns:
            Energy level
        """
        # Convert bytes to int16 values for energy calculation
        count = len(data) // 2
        format_str = f"{count}h"
        shorts = struct.unpack(format_str, data)
        
        # Calculate RMS as energy
        sum_squares = sum(s * s for s in shorts)
        return (sum_squares / count) ** 0.5 if count > 0 else 0
    
    def _recognize(self, audio_data: bytes) -> Optional[str]:
        """
        Recognize speech using DeepSpeech
        
        Args:
            audio_data: Recorded audio data
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            # DeepSpeech needs 16-bit, 16kHz, mono PCM
            # Write data to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
                
                with wave.open(wav_path, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.RATE)
                    wf.writeframes(audio_data)
            
            # Read the WAV file as 16-bit PCM
            with wave.open(wav_path, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                buffer = np.frombuffer(frames, dtype=np.int16)
            
            # Delete temporary file
            os.unlink(wav_path)
            
            # Perform speech recognition
            text = self.model.stt(buffer)
            
            if not text:
                logger.debug("No speech recognized by DeepSpeech")
                return None
                
            logger.debug(f"DeepSpeech recognized: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"DeepSpeech recognition error: {e}")
            return None
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()