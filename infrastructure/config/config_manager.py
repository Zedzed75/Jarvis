"""
Configuration Manager for Jarvis

Implements the ConfigManagerInterface to provide configuration services.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from domain.interfaces.repositories import ConfigManagerInterface

logger = logging.getLogger('jarvis.infrastructure.config')

class ConfigManager(ConfigManagerInterface):
    """
    Manages configuration settings for Jarvis assistant
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to the main configuration file
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.config_path = config_path
        self.config = {}
        self.secrets = {}
        
        # Load configuration
        self._load_config()
        
        # Try to load secrets
        self._load_secrets()
        
        # Merge environment variables into config
        self._merge_env_vars()
        
        logger.info("Configuration manager initialized")
    
    def _load_config(self) -> None:
        """Load main configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                
            logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_secrets(self) -> None:
        """Try to load secrets configuration file if it exists"""
        # Determine secrets path based on main config path
        config_dir = os.path.dirname(self.config_path)
        secrets_path = os.path.join(config_dir, 'secrets.yaml')
        
        if not os.path.exists(secrets_path):
            logger.warning(f"Secrets file not found at {secrets_path}")
            return
            
        try:
            with open(secrets_path, 'r') as f:
                self.secrets = yaml.safe_load(f)
                
            logger.info(f"Secrets loaded from {secrets_path}")
            
            # Merge secrets into config
            self._merge_secrets()
            
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
    
    def _merge_secrets(self) -> None:
        """Merge secrets into the configuration"""
        self._merge_dict(self.config, self.secrets)
        logger.debug("Secrets merged into configuration")
    
    def _merge_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source dictionary into target dictionary
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                self._merge_dict(target[key], value)
            else:
                # Overwrite or add values
                target[key] = value
    
    def _merge_env_vars(self) -> None:
        """Merge environment variables into configuration"""
        # Example of mapping env vars to config paths
        env_mapping = {
            'OPENWEATHERMAP_API_KEY': 'skills.weather.api_key',
            'TELEGRAM_BOT_TOKEN': 'notifications.telegram.token',
            'TELEGRAM_CHAT_ID': 'notifications.telegram.chat_id',
            'LOG_LEVEL': 'general.log_level',
            'MEMORY_STORAGE_PATH': 'memory.storage_path',
            'DEEPSPEEECH_MODEL_PATH': 'speech.recognition.deepspeech_model_path',
            'MOZILLA_TTS_MODEL_PATH': 'speech.synthesis.mozilla_tts_model_path',
            'ENABLE_TELEGRAM_NOTIFICATIONS': 'notifications.enabled',
            'ENABLE_SPEECH_RECOGNITION': 'speech.recognition.enabled',
            'ENABLE_TEXT_TO_SPEECH': 'speech.synthesis.enabled',
            'ENABLE_WAKE_WORD': 'speech.wake_word.enabled'
        }
        
        for env_var, config_path in env_mapping.items():
            if env_var in os.environ:
                # Convert environment variables to appropriate types
                value = os.environ[env_var]
                
                # Handle boolean values
                if value.lower() in ('true', 'yes', '1'):
                    value = True
                elif value.lower() in ('false', 'no', '0'):
                    value = False
                
                # Set the value in config
                self._set_config_path(config_path, value)
                
        logger.debug("Environment variables merged into configuration")
    
    def _set_config_path(self, path: str, value: Any) -> None:
        """
        Set a value in the config dictionary based on dot-separated path
        
        Args:
            path: Dot-separated path to the configuration value
            value: Value to set
        """
        parts = path.split('.')
        d = self.config
        
        # Navigate to the right level
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
            
        # Set the value
        d[parts[-1]] = value
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration
        
        Returns:
            Complete configuration dictionary
        """
        return self.config
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated path
        
        Args:
            key_path: Dot-separated path to the configuration value
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        result = self.config
        
        # Navigate through the dictionary
        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return default
                
        return result
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        Save the current configuration to file
        
        Args:
            config_path: Path to save the configuration (default: original path)
            
        Returns:
            True if successful, False otherwise
        """
        path = config_path or self.config_path
        
        try:
            with open(path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                
            logger.info(f"Configuration saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False