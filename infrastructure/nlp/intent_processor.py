"""
Intent Processor Implementation for Jarvis

This module implements the IntentRecognizerInterface to recognize intents
from natural language input using rule-based or model-based approaches.
"""

import re
import logging
from typing import Dict, Any, List, Optional

# Conditionally import Rasa
try:
    from rasa.nlu.model import Interpreter
    RASA_AVAILABLE = True
except ImportError:
    RASA_AVAILABLE = False

# Conditionally import DialogFlow
try:
    from google.cloud import dialogflow
    DIALOGFLOW_AVAILABLE = True
except ImportError:
    DIALOGFLOW_AVAILABLE = False

from domain.interfaces.repositories import IntentRecognizerInterface

logger = logging.getLogger('jarvis.infrastructure.nlp.intent_processor')

class RuleBasedIntentProcessor(IntentRecognizerInterface):
    """
    Rule-based implementation of intent recognition
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the rule-based intent processor
        
        Args:
            config: Configuration dictionary for intent processing
        """
        self.config = config
        self.threshold = config.get('confidence_threshold', 0.6)
        self.fallback_intent = config.get('fallback_intent', 'unknown')
        
        # Load intent rules from config or default
        self.rules = config.get('rules', {})
        
        # If no rules provided in config, use some defaults
        if not self.rules:
            self.rules = self._get_default_rules()
            
        logger.info(f"Rule-based intent processor initialized with {len(self.rules)} rules")

    def _get_default_rules(self) -> Dict[str, List[str]]:
        """
        Get default intent rules
        
        Returns:
            Dictionary mapping intents to trigger phrases
        """
        return {
            'weather': [
                'weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy',
                'how hot', 'how cold', 'how warm', 'precipitation'
            ],
            'time': [
                'time', 'hour', 'clock', 'what time'
            ],
            'date': [
                'date', 'day', 'month', 'year', 'today', 'tomorrow', 'yesterday',
                'what day'
            ],
            'greeting': [
                'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon',
                'good evening', 'howdy', 'sup'
            ],
            'farewell': [
                'goodbye', 'bye', 'see you', 'later', 'good night', 'farewell'
            ],
            'gratitude': [
                'thank', 'thanks', 'appreciate', 'grateful'
            ],
            'calendar': [
                'calendar', 'schedule', 'appointment', 'meeting', 'event', 'reminder',
                'remind me'
            ],
            'search': [
                'search', 'find', 'look up', 'google', 'information about', 'tell me about'
            ],
            'home': [
                'turn on', 'turn off', 'dim', 'brighten', 'set', 'lock', 'unlock',
                'open', 'close', 'lights', 'thermostat', 'temperature'
            ]
        }
    
    def recognize_intent(self, text: str) -> str:
        """
        Recognize intent from text
        
        Args:
            text: User input text
            
        Returns:
            Recognized intent
        """
        try:
            # Convert to lowercase for matching
            text_lower = text.lower()
            
            # Calculate match scores for each intent
            intent_scores = {}
            
            for intent, phrases in self.rules.items():
                score = 0
                max_phrase_score = 0
                
                for phrase in phrases:
                    phrase_lower = phrase.lower()
                    
                    # Calculate match score based on phrase presence
                    if phrase_lower in text_lower:
                        # Full phrase match is weighted higher
                        phrase_score = len(phrase) / len(text) * 2
                        max_phrase_score = max(max_phrase_score, phrase_score)
                
                intent_scores[intent] = max_phrase_score
            
            # Find the intent with the highest score
            best_intent = self.fallback_intent
            best_score = 0
            
            for intent, score in intent_scores.items():
                if score > best_score:
                    best_score = score
                    best_intent = intent
            
            # Check against confidence threshold
            if best_score < self.threshold:
                logger.debug(f"No intent matched with sufficient confidence. Best: {best_intent} ({best_score:.2f})")
                return self.fallback_intent
                
            logger.debug(f"Recognized intent: {best_intent} (score: {best_score:.2f})")
            return best_intent
            
        except Exception as e:
            logger.error(f"Intent recognition error: {e}")
            return self.fallback_intent


class RasaIntentProcessor(IntentRecognizerInterface):
    """
    Rasa NLU-based implementation of intent recognition
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Rasa intent processor
        
        Args:
            config: Configuration dictionary for intent processing
        """
        if not RASA_AVAILABLE:
            raise ImportError("Rasa NLU is not available. Please install Rasa to use this processor.")
            
        self.config = config
        self.threshold = config.get('confidence_threshold', 0.6)
        self.fallback_intent = config.get('fallback_intent', 'unknown')
        
        # Load Rasa model
        model_path = config.get('rasa_model_path')
        if not model_path:
            raise ValueError("Rasa model path not provided")
            
        self.interpreter = Interpreter.load(model_path)
        logger.info(f"Rasa intent processor initialized with model: {model_path}")
    
    def recognize_intent(self, text: str) -> str:
        """
        Recognize intent from text using Rasa NLU
        
        Args:
            text: User input text
            
        Returns:
            Recognized intent
        """
        try:
            # Get prediction from Rasa
            result = self.interpreter.parse(text)
            
            # Check confidence threshold
            intent_name = result.get('intent', {}).get('name', self.fallback_intent)
            confidence = result.get('intent', {}).get('confidence', 0.0)
            
            if confidence < self.threshold:
                logger.debug(f"Low confidence ({confidence:.2f}) for intent: {intent_name}")
                return self.fallback_intent
                
            logger.debug(f"Recognized intent: {intent_name} (confidence: {confidence:.2f})")
            return intent_name
            
        except Exception as e:
            logger.error(f"Rasa intent recognition error: {e}")
            return self.fallback_intent


class DialogFlowIntentProcessor(IntentRecognizerInterface):
    """
    DialogFlow-based implementation of intent recognition
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DialogFlow intent processor
        
        Args:
            config: Configuration dictionary for intent processing
        """
        if not DIALOGFLOW_AVAILABLE:
            raise ImportError("DialogFlow is not available. Please install google-cloud-dialogflow to use this processor.")
            
        self.config = config
        self.threshold = config.get('confidence_threshold', 0.6)
        self.fallback_intent = config.get('fallback_intent', 'unknown')
        
        # Initialize DialogFlow
        project_id = config.get('dialogflow_project_id')
        if not project_id:
            raise ValueError("DialogFlow project ID not provided")
            
        # Set credentials path if provided
        credentials_file = config.get('dialogflow_credentials_file')
        if credentials_file:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            
        self.language = config.get('dialogflow_language', 'en')
        self.session_client = dialogflow.SessionsClient()
        self.session = f"projects/{project_id}/agent/sessions/jarvis-session"
        
        logger.info(f"DialogFlow intent processor initialized for project: {project_id}")
    
    def recognize_intent(self, text: str) -> str:
        """
        Recognize intent from text using DialogFlow
        
        Args:
            text: User input text
            
        Returns:
            Recognized intent
        """
        try:
            # Build the text input
            text_input = dialogflow.TextInput(text=text, language_code=self.language)
            query_input = dialogflow.QueryInput(text=text_input)
            
            # Detect intent
            response = self.session_client.detect_intent(
                request={"session": self.session, "query_input": query_input}
            )
            
            # Extract intent information
            result = response.query_result
            intent_name = result.intent.display_name
            confidence = result.intent_detection_confidence
            
            if confidence < self.threshold:
                logger.debug(f"Low confidence ({confidence:.2f}) for intent: {intent_name}")
                return self.fallback_intent
                
            logger.debug(f"Recognized intent: {intent_name} (confidence: {confidence:.2f})")
            return intent_name
            
        except Exception as e:
            logger.error(f"DialogFlow intent recognition error: {e}")
            return self.fallback_intent