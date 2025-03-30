"""
Conversation Service for Jarvis

This service manages the conversation flow using clean architecture principles.
It coordinates language processing and skill execution.
"""

import logging
import random
from typing import Dict, Any, List, Optional

from domain.interfaces.repositories import IntentRecognizerInterface, EntityExtractorInterface
from domain.interfaces.skills import SkillInterface
from domain.models.user import User, Interaction

logger = logging.getLogger('jarvis.application.services.conversation')

class ConversationService:
    """
    Service for managing conversation state and flow
    """
    
    def __init__(self, intent_recognizer: IntentRecognizerInterface, 
                entity_extractor: EntityExtractorInterface,
                user: User):
        """
        Initialize the conversation service
        
        Args:
            intent_recognizer: Component for intent recognition
            entity_extractor: Component for entity extraction
            user: User entity for conversation context
        """
        self.intent_recognizer = intent_recognizer
        self.entity_extractor = entity_extractor
        self.user = user
        
        # Default responses for when no skill can handle the request
        self.default_responses = [
            "I'm not sure how to help with that.",
            "I didn't understand that request.",
            "Could you phrase that differently?",
            "I'm still learning how to handle that type of request."
        ]
        
        logger.info("Conversation service initialized")
    
    def process_command(self, command: str, skills: Dict[str, SkillInterface]) -> str:
        """
        Process a user command to generate a response
        
        Args:
            command: User's text command
            skills: Dictionary of available skills
            
        Returns:
            Assistant's response text
        """
        try:
            # Recognize intent
            intent = self.intent_recognizer.recognize_intent(command)
            logger.debug(f"Recognized intent: {intent}")
            
            # Extract entities
            entities = self.entity_extractor.extract_entities(command)
            logger.debug(f"Extracted entities: {entities}")
            
            # Try to find a skill that can handle this intent/entities
            response = self._handle_with_skills(command, intent, entities, skills)
            
            # If no skill could handle it, use a default response
            if not response:
                response = self._get_default_response()
            
            # Record the interaction
            interaction = Interaction(
                user_input=command,
                assistant_response=response,
                intent=intent,
                entities=entities
            )
            self.user.add_interaction(interaction)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return "I'm sorry, I encountered an error while processing your request."
    
    def _handle_with_skills(self, command: str, intent: str, entities: Dict[str, Any], 
                          skills: Dict[str, SkillInterface]) -> Optional[str]:
        """
        Try to handle the command with available skills
        
        Args:
            command: User's command
            intent: Recognized intent
            entities: Extracted entities
            skills: Available skills
            
        Returns:
            Response text or None if no skill could handle it
        """
        # First, check if any skill declares it can handle this intent/entities
        for skill_name, skill in skills.items():
            if skill.can_handle(intent, entities):
                logger.debug(f"Skill {skill_name} can handle this request")
                response = skill.process(command, intent, entities)
                if response:
                    return response
        
        # If no skill explicitly handled it, try to infer the best skill
        # based on intent mapping
        intent_to_skill = {
            'weather': 'weather',
            'time': 'time_date',
            'date': 'time_date',
            'greeting': 'personality',
            'farewell': 'personality'
            # Add more mappings as skills are added
        }
        
        if intent in intent_to_skill and intent_to_skill[intent] in skills:
            skill_name = intent_to_skill[intent]
            skill = skills[skill_name]
            logger.debug(f"Trying skill {skill_name} based on intent mapping")
            response = skill.process(command, intent, entities)
            if response:
                return response
        
        # No skill could handle the request
        return None
    
    def _get_default_response(self) -> str:
        """
        Get a default response for when no skill can handle the request
        
        Returns:
            Default response text
        """
        return random.choice(self.default_responses)