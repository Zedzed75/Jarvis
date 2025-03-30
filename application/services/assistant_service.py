"""
Assistant Service for Jarvis

This is the main application service that coordinates the assistant's behavior.
It follows clean architecture principles by orchestrating the use of domain
entities and infrastructure services.
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional

from domain.interfaces.repositories import SpeechRecognizerInterface, TextToSpeechInterface, WakeWordDetectorInterface
from domain.interfaces.skills import SkillInterface
from application.services.notification_service import NotificationService
from application.services.memory_service import MemoryService
from application.services.conversation_service import ConversationService

logger = logging.getLogger('jarvis.application.services.assistant')

class AssistantService:
    """
    Main assistant service that coordinates the behavior of Jarvis
    """
    
    def __init__(self, config: Dict[str, Any], text_mode: bool = False, notification_service: Optional[NotificationService] = None):
        """
        Initialize the assistant service
        
        Args:
            config: Configuration dictionary
            text_mode: If True, use text input/output instead of voice
            notification_service: Optional notification service
        """
        self.config = config
        self.text_mode = text_mode
        self.notification_service = notification_service
        self.running = False
        
        # These will be injected from factories in the infrastructure layer
        self.speech_recognizer = None
        self.text_to_speech = None
        self.wake_word_detector = None
        self.memory_service = None
        self.conversation_service = None
        self.skills = {}
        
        logger.info("Assistant service initialized")
    
    def set_speech_components(self, recognizer: SpeechRecognizerInterface,
                           synthesizer: TextToSpeechInterface,
                           wake_detector: WakeWordDetectorInterface) -> None:
        """
        Set speech components using dependency injection
        
        Args:
            recognizer: Speech recognition component
            synthesizer: Text-to-speech component
            wake_detector: Wake word detection component
        """
        self.speech_recognizer = recognizer
        self.text_to_speech = synthesizer
        self.wake_word_detector = wake_detector
        logger.debug("Speech components injected")
    
    def set_services(self, memory_service: MemoryService,
                   conversation_service: ConversationService) -> None:
        """
        Set application services using dependency injection
        
        Args:
            memory_service: Memory service for context and history
            conversation_service: Conversation service for dialogue management
        """
        self.memory_service = memory_service
        self.conversation_service = conversation_service
        logger.debug("Application services injected")
    
    def register_skill(self, skill_name: str, skill: SkillInterface) -> None:
        """
        Register a skill
        
        Args:
            skill_name: Name of the skill
            skill: Skill implementation
        """
        self.skills[skill_name] = skill
        logger.debug(f"Skill registered: {skill_name}")
    
    def start(self) -> None:
        """Start the assistant"""
        self.running = True
        
        # Startup message
        if not self.text_mode:
            self.respond("Jarvis online. How may I assist you?")
        else:
            print("Jarvis online. How may I assist you?")
            
        if not self.text_mode and self.wake_word_detector:
            # Start wake word detection in a separate thread
            wake_thread = threading.Thread(target=self._wake_word_loop)
            wake_thread.daemon = True
            wake_thread.start()
            
            # Main loop waits for wake thread to signal
            while self.running:
                time.sleep(0.1)
        else:
            # Text mode main loop
            self._text_loop()
    
    def stop(self) -> None:
        """Stop the assistant"""
        self.running = False
        
        # Notify about shutdown if notification service is available
        if self.notification_service:
            self.notification_service.notify("Jarvis is shutting down.", "low")
            
        logger.info("Assistant shutting down")
    
    def _wake_word_loop(self) -> None:
        """Continuous loop for wake word detection"""
        logger.info("Wake word detection started")
        
        while self.running:
            try:
                # Wait for wake word
                if self.wake_word_detector.detect():
                    logger.info("Wake word detected")
                    
                    # Acknowledge wake
                    if self.text_to_speech:
                        self.text_to_speech.speak("Yes?")
                    
                    # Listen for command
                    if self.speech_recognizer:
                        command = self.speech_recognizer.listen()
                        if command:
                            self._process_command(command)
                    else:
                        logger.error("Speech recognizer not initialized")
                        
            except Exception as e:
                logger.error(f"Error in wake word loop: {e}")
                time.sleep(1)  # Prevent tight loop on error
    
    def _text_loop(self) -> None:
        """Text-based interaction loop"""
        logger.info("Text mode enabled")
        
        while self.running:
            try:
                # Get input from user
                command = input("You: ")
                
                if command.lower() in ['exit', 'quit', 'bye']:
                    self.stop()
                    break
                    
                self._process_command(command)
                
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in text loop: {e}")
    
    def _process_command(self, command: str) -> None:
        """
        Process a user command
        
        Args:
            command: User's command as text
        """
        try:
            logger.info(f"Processing command: {command}")
            
            # Use conversation service to determine intent and response
            if self.conversation_service:
                response = self.conversation_service.process_command(command, self.skills)
            else:
                response = "I'm sorry, my conversation processing is not available at the moment."
            
            # Respond to the user
            self.respond(response)
            
            # Save to memory if available
            if self.memory_service:
                # In a real implementation, we would save the full context
                # including intent and entities
                self.memory_service.save_interaction(command, response, "unknown", {})
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.respond("I'm sorry, I encountered an error processing your request.")
    
    def respond(self, text: str) -> None:
        """
        Respond to the user
        
        Args:
            text: Response text
        """
        logger.info(f"Jarvis response: {text}")
        
        if self.text_mode:
            print(f"Jarvis: {text}")
        elif self.text_to_speech:
            self.text_to_speech.speak(text)
        else:
            logger.error("Unable to respond (no text-to-speech service available)")