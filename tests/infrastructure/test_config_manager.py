"""
Tests for the Configuration Manager
"""

import os
import unittest
import tempfile
import yaml
from infrastructure.config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test config files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'assistant.yaml')
        self.secrets_path = os.path.join(self.temp_dir.name, 'secrets.yaml')
        
        # Create test config data
        self.config_data = {
            'general': {
                'name': 'TestJarvis',
                'log_level': 'info'
            },
            'speech': {
                'recognition': {
                    'provider': 'google'
                }
            }
        }
        
        # Create test secrets data
        self.secrets_data = {
            'speech': {
                'recognition': {
                    'google_api_key': 'test_api_key'
                }
            }
        }
        
        # Write test config files
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f)
            
        with open(self.secrets_path, 'w') as f:
            yaml.dump(self.secrets_data, f)
        
        # Create config manager
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_load_config(self):
        # Verify config was loaded
        self.assertEqual(self.config_manager.config['general']['name'], 'TestJarvis')
        self.assertEqual(self.config_manager.config['speech']['recognition']['provider'], 'google')
    
    def test_load_secrets(self):
        # Verify secrets were loaded and merged
        self.assertEqual(
            self.config_manager.config['speech']['recognition']['google_api_key'],
            'test_api_key'
        )
    
    def test_get_config(self):
        # Get the complete config
        config = self.config_manager.get_config()
        
        # Verify it contains merged data
        self.assertEqual(config['general']['name'], 'TestJarvis')
        self.assertEqual(config['speech']['recognition']['google_api_key'], 'test_api_key')
    
    def test_get_value(self):
        # Test getting values with dot notation
        self.assertEqual(
            self.config_manager.get_value('general.name'),
            'TestJarvis'
        )
        
        self.assertEqual(
            self.config_manager.get_value('speech.recognition.provider'),
            'google'
        )
        
        self.assertEqual(
            self.config_manager.get_value('speech.recognition.google_api_key'),
            'test_api_key'
        )
    
    def test_get_value_with_default(self):
        # Test getting non-existent value with default
        self.assertEqual(
            self.config_manager.get_value('non_existent', 'default_value'),
            'default_value'
        )
    
    def test_save_config(self):
        # Modify config
        self.config_manager.config['general']['name'] = 'NewName'
        
        # Save config
        self.config_manager.save_config()
        
        # Load config again to verify changes were saved
        new_config_manager = ConfigManager(self.config_path)
        self.assertEqual(new_config_manager.config['general']['name'], 'NewName')


if __name__ == '__main__':
    unittest.main()