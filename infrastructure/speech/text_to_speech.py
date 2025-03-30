"""
Text-to-Speech Implementation for Jarvis

This module implements the TextToSpeechInterface using
Amazon Polly or Mozilla TTS.
"""

import os
import io
import wave
import logging
import tempfile
from typing import Dict, Any, Optional

import pyaudio

# Conditionally import Amazon Polly
try:
    import boto3
    POLLY_AVAILABLE = True
except ImportError:
    POLLY_AVAILABLE = False

# Conditionally import Mozilla TTS
try:
    from TTS.api import TTS
    MOZILLA_TTS_AVAILABLE = True
except ImportError:
    MOZILLA_TTS_AVAILABLE = False

from domain.interfaces.repositories import TextToSpeechInterface

logger = logging.getLogger('jarvis.infrastructure.speech.synthesis')

class PollyTextToSpeech(TextToSpeechInterface):
    """
    Amazon Polly implementation of text-to-speech
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Amazon Polly TTS
        
        Args:
            config: Configuration dictionary
        """
        if not POLLY_AVAILABLE:
            raise ImportError("Amazon Polly is not available. Please install boto3.")
            
        self.config = config
        self.voice = config.get('voice', 'Brian')
        self.audio = pyaudio.PyAudio()
        
        # AWS credentials
        aws_access_key = config.get('aws_access_key_id')
        aws_secret_key = config.get('aws_secret_access_key')
        region_name = config.get('aws_region', 'us-east-1')
        
        if aws_access_key and aws_secret_key:
            self.polly_client = boto3.client(
                'polly',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name
            )
        else:
            # Use AWS credentials from environment or ~/.aws/
            self.polly_client = boto3.client('polly', region_name=region_name)
            
        # Configure Polly parameters
        self.engine = config.get('polly_engine', 'neural')
        self.language = config.get('polly_language', 'en-US')
        
        logger.info(f"Amazon Polly TTS initialized with voice: {self.voice}")
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add SSML markup for better speech
            ssml_text = f"""
            <speak>
                {text}
            </speak>
            """
            
            # Request speech synthesis
            response = self.polly_client.synthesize_speech(
                Engine=self.engine,
                LanguageCode=self.language,
                OutputFormat='pcm',
                SampleRate='16000',
                Text=ssml_text,
                TextType='ssml',
                VoiceId=self.voice
            )
            
            # Check if audio stream is available
            if "AudioStream" not in response:
                logger.error("No AudioStream in Polly response")
                return False
                
            # Get audio data
            audio_data = response["AudioStream"].read()
            
            # Play audio
            self._play_audio(audio_data)
            return True
            
        except Exception as e:
            logger.error(f"Polly TTS error: {e}")
            return False
    
    def _play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data through speakers
        
        Args:
            audio_data: Audio data to play
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True
            )
            
            # Play audio
            stream.write(audio_data)
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()


class MozillaTTS(TextToSpeechInterface):
    """
    Mozilla TTS implementation of text-to-speech
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Mozilla TTS
        
        Args:
            config: Configuration dictionary
        """
        if not MOZILLA_TTS_AVAILABLE:
            raise ImportError("Mozilla TTS is not available. Please install TTS.")
            
        self.config = config
        self.audio = pyaudio.PyAudio()
        
        # Initialize Mozilla TTS
        model_name = config.get('mozilla_tts_model', 'tts_models/en/ljspeech/tacotron2-DDC')
        vocoder_name = config.get('mozilla_tts_vocoder', 'vocoder_models/en/ljspeech/multiband-melgan')
        
        # If local model path is provided, use it instead
        model_path = config.get('mozilla_tts_model_path')
        if model_path and os.path.exists(model_path):
            self.tts = TTS(model_path=model_path)
        else:
            # Use pre-trained model
            self.tts = TTS(model_name=model_name, vocoder_name=vocoder_name)
            
        logger.info("Mozilla TTS initialized")
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
            
            # Generate speech to the temporary file
            self.tts.tts_to_file(text, file_path=wav_path)
            
            # Play the generated audio
            self._play_wav_file(wav_path)
            
            # Clean up temporary file
            os.unlink(wav_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Mozilla TTS error: {e}")
            return False
    
    def _play_wav_file(self, wav_path: str) -> None:
        """
        Play a WAV file through speakers
        
        Args:
            wav_path: Path to WAV file
        """
        try:
            # Open the WAV file
            with wave.open(wav_path, 'rb') as wf:
                # Get WAV parameters
                channels = wf.getnchannels()
                width = wf.getsampwidth()
                rate = wf.getframerate()
                
                # Set PyAudio format based on sample width
                format_mapping = {
                    1: pyaudio.paInt8,
                    2: pyaudio.paInt16,
                    4: pyaudio.paFloat32
                }
                audio_format = format_mapping.get(width, pyaudio.paInt16)
                
                # Open audio stream
                stream = self.audio.open(
                    format=audio_format,
                    channels=channels,
                    rate=rate,
                    output=True
                )
                
                # Read and play chunks of audio
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                # Close stream
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            logger.error(f"Error playing WAV file: {e}")
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()