"""
Entity Extractor Implementation for Jarvis

This module implements the EntityExtractorInterface to extract entities
from natural language input using rule-based or model-based approaches.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Conditionally import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from domain.interfaces.repositories import EntityExtractorInterface

logger = logging.getLogger('jarvis.infrastructure.nlp.entity_extractor')

class RuleBasedEntityExtractor(EntityExtractorInterface):
    """
    Rule-based implementation of entity extraction using regular expressions
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the rule-based entity extractor
        
        Args:
            config: Configuration dictionary for entity extraction
        """
        self.config = config
        
        # Compile regular expressions for different entity types
        self.patterns = {
            'date': [
                # Today, tomorrow, yesterday
                r'\b(today|tomorrow|yesterday)\b',
                # Day of week
                r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                # Month/Day/Year formats
                r'\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-](\d{4}|\d{2})\b',
                # Month Day, Year
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b',
            ],
            'time': [
                # HH:MM format with optional AM/PM
                r'\b([01]?\d|2[0-3]):([0-5]\d)(?:\s*([ap]\.?m\.?))?',
                # Natural language time references
                r'\b(noon|midnight)\b',
                r'\b([1-9]|1[0-2])\s*([ap]\.?m\.?)\b',
            ],
            'duration': [
                # X minutes/hours/days/weeks/months/years
                r'\b(\d+)\s+(minutes?|hours?|days?|weeks?|months?|years?)\b',
            ],
            'location': [
                # Simple location patterns
                r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ],
            'temperature': [
                # Temperature values with units
                r'\b(\d+(?:\.\d+)?)\s*(?:degrees?|°)\s*([CF])\b',
            ],
        }
        
        # Add custom patterns from config
        custom_patterns = config.get('custom_patterns', {})
        for entity_type, patterns in custom_patterns.items():
            if entity_type not in self.patterns:
                self.patterns[entity_type] = []
            self.patterns[entity_type].extend(patterns)
        
        # Compile all regex patterns
        self.compiled_patterns = {}
        for entity_type, patterns in self.patterns.items():
            self.compiled_patterns[entity_type] = [re.compile(p, re.IGNORECASE) for p in patterns]
            
        logger.info("Rule-based entity extractor initialized")
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text
        
        Args:
            text: User input text
            
        Returns:
            Dictionary of extracted entities
        """
        try:
            entities = {}
            
            # Process each entity type
            for entity_type, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    matches = pattern.findall(text)
                    if matches:
                        # Process matches based on entity type
                        if entity_type == 'date':
                            entities['date'] = self._process_date_match(matches[0], text)
                        elif entity_type == 'time':
                            entities['time'] = self._process_time_match(matches[0], text)
                        elif entity_type == 'duration':
                            entities['duration'] = self._process_duration_match(matches[0])
                        elif entity_type == 'location':
                            # For location, just take the captured group
                            if isinstance(matches[0], tuple):
                                entities['location'] = matches[0][0]
                            else:
                                entities['location'] = matches[0]
                        elif entity_type == 'temperature':
                            # For temperature, include the value and unit
                            if isinstance(matches[0], tuple):
                                value, unit = matches[0]
                                entities['temperature'] = {
                                    'value': float(value),
                                    'unit': unit.upper()
                                }
                            
                        # Break after first match for this entity type
                        break
                    
            # Extract potential items (nouns preceded by articles or adjectives)
            item_pattern = re.compile(r'\b(the|a|an|my|this|that)\s+(?:\w+\s+){0,2}(\w+)\b', re.IGNORECASE)
            item_matches = item_pattern.findall(text)
            if item_matches and 'item' not in entities:
                entities['item'] = item_matches[0][1]
                
            logger.debug(f"Extracted entities: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return {}
    
    def _process_date_match(self, match: Any, text: str) -> str:
        """
        Process a date match to a standardized format
        
        Args:
            match: Regex match object or string
            text: Original text
            
        Returns:
            Standardized date string
        """
        today = datetime.now()
        
        # Handle simple relative dates
        if isinstance(match, str):
            lowered = match.lower()
            if lowered == 'today':
                return today.strftime('%Y-%m-%d')
            elif lowered == 'tomorrow':
                tomorrow = today + timedelta(days=1)
                return tomorrow.strftime('%Y-%m-%d')
            elif lowered == 'yesterday':
                yesterday = today - timedelta(days=1)
                return yesterday.strftime('%Y-%m-%d')
                
            # Day of week handling would need more complex logic
            # to determine next occurrence of that day
                
        # For more complex date formats, return as is for now
        # In a real system, we'd parse and standardize
        return str(match)
    
    def _process_time_match(self, match: Any, text: str) -> str:
        """
        Process a time match to a standardized format
        
        Args:
            match: Regex match object or tuple
            text: Original text
            
        Returns:
            Standardized time string
        """
        # For simple time references
        if isinstance(match, str):
            if match.lower() == 'noon':
                return '12:00'
            elif match.lower() == 'midnight':
                return '00:00'
                
        # For more complex time formats (HH:MM AM/PM)
        # In a real system, we'd convert to 24-hour format
        return str(match)
    
    def _process_duration_match(self, match: tuple) -> Dict[str, Any]:
        """
        Process a duration match to a standardized format
        
        Args:
            match: Tuple with (value, unit)
            
        Returns:
            Duration dictionary
        """
        value = int(match[0])
        unit = match[1].rstrip('s')  # Remove plural 's' if present
        
        return {
            'value': value,
            'unit': unit
        }


class SpacyEntityExtractor(EntityExtractorInterface):
    """
    spaCy-based implementation of entity extraction
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the spaCy entity extractor
        
        Args:
            config: Configuration dictionary for entity extraction
        """
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy is not available. Please install spaCy to use this extractor.")
            
        self.config = config
        model_name = config.get('spacy_model', 'en_core_web_md')
        
        # Load spaCy model
        self.nlp = spacy.load(model_name)
        
        logger.info(f"spaCy entity extractor initialized with model: {model_name}")
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text using spaCy
        
        Args:
            text: User input text
            
        Returns:
            Dictionary of extracted entities
        """
        try:
            doc = self.nlp(text)
            entities = {}
            
            # Process named entities
            for ent in doc.ents:
                entity_type = ent.label_.lower()
                
                # Map spaCy entity types to our entity types
                if entity_type in ['date', 'time']:
                    entities[entity_type] = ent.text
                elif entity_type in ['gpe', 'loc', 'fac']:
                    entities['location'] = ent.text
                elif entity_type == 'cardinal' and 'degree' in text[ent.end:ent.end+10].lower():
                    entities['temperature'] = ent.text
                elif entity_type == 'money':
                    entities['amount'] = ent.text
                elif entity_type == 'person':
                    entities['person'] = ent.text
                elif entity_type == 'org':
                    entities['organization'] = ent.text
                    
            # Process noun chunks for potential entities
            for chunk in doc.noun_chunks:
                # Check if this chunk might be an item or object
                if chunk.root.pos_ == 'NOUN' and 'item' not in entities:
                    entities['item'] = chunk.text
                    
            logger.debug(f"Extracted entities with spaCy: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"spaCy entity extraction error: {e}")
            return {}