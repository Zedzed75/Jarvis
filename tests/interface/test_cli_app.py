"""
Tests for the CLI Application
"""

import unittest
from unittest.mock import patch, Mock
from interface.cli.cli_app import JarvisCLI

class TestJarvisCLI(unittest.TestCase):
    
    def setUp(self):
        # Create mock assistant service
        self.mock_assistant = Mock()
        
        # Create CLI app
        self.cli = JarvisCLI(self.mock_assistant)
        
        # Setup the process_command mock
        self.cli._process_command = Mock(return_value="Test response")
    
    def test_initialization(self):
        # Verify assistant service was set
        self.assertEqual(self.cli.assistant, self.mock_assistant)
    
    @patch('builtins.input', side_effect=["test command", "exit"])
    @patch('builtins.print')
    def test_run(self, mock_print, mock_input):
        # Run CLI app
        self.cli.run()
        
        # Verify _process_command was called
        self.cli._process_command.assert_called_once_with("test command")
        
        # Verify response was printed
        mock_print.assert_any_call("Jarvis: Test response")
    
    @patch('builtins.input', side_effect=["quit"])
    @patch('builtins.print')
    def test_run_quit(self, mock_print, mock_input):
        # Run CLI app
        self.cli.run()
        
        # Verify goodbye message was printed
        mock_print.assert_any_call("Jarvis: Goodbye!")
        
        # Verify _process_command was not called
        self.cli._process_command.assert_not_called()
    
    @patch('builtins.input', side_effect=["bye"])
    @patch('builtins.print')
    def test_run_bye(self, mock_print, mock_input):
        # Run CLI app
        self.cli.run()
        
        # Verify goodbye message was printed
        mock_print.assert_any_call("Jarvis: Goodbye!")
        
        # Verify _process_command was not called
        self.cli._process_command.assert_not_called()
    
    @patch('builtins.input', side_effect=["exit"])
    @patch('builtins.print')
    def test_run_exit(self, mock_print, mock_input):
        # Run CLI app
        self.cli.run()
        
        # Verify goodbye message was printed
        mock_print.assert_any_call("Jarvis: Goodbye!")
        
        # Verify _process_command was not called
        self.cli._process_command.assert_not_called()
    
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        # Run CLI app
        self.cli.run()
        
        # Verify goodbye message was printed
        mock_print.assert_any_call("\nJarvis: Goodbye!")
    
    @patch('builtins.input', side_effect=Exception("Test error"))
    @patch('builtins.print')
    def test_run_exception(self, mock_print, mock_input):
        # Run CLI app with exception in input
        self.cli.run()
        
        # Verify error message was printed
        mock_print.assert_any_call("Jarvis: I'm sorry, I encountered an error.")
    
    def test_process_command_calls_assistant(self):
        # Configure assistant service mock
        self.mock_assistant.process_command = Mock(return_value="Assistant response")
        
        # Reset the process_command mock to use the real method
        self.cli._process_command = self.cli.__class__._process_command.__get__(self.cli, self.cli.__class__)
        
        # Process command
        response = self.cli._process_command("test command")
        
        # Verify assistant was called
        self.mock_assistant.process_command.assert_called_once_with("test command")
        
        # Verify response
        self.assertEqual(response, "Assistant response")
    
    def test_process_command_handles_exception(self):
        # Configure assistant service mock to raise exception
        self.mock_assistant.process_command = Mock(side_effect=Exception("Test error"))
        
        # Reset the process_command mock to use the real method
        self.cli._process_command = self.cli.__class__._process_command.__get__(self.cli, self.cli.__class__)
        
        # Process command
        response = self.cli._process_command("test command")
        
        # Verify error response
        self.assertEqual(response, "I'm sorry, I encountered an error processing your request.")


if __name__ == '__main__':
    unittest.main()