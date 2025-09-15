"""
Unit tests for main module

Tests the main entry point and overall application flow.
"""

import unittest
from unittest.mock import patch, Mock
import main


class TestMain(unittest.TestCase):
    """Test cases for the main module."""
    
    @patch('main.ConsoleApp')
    def test_main_function(self, mock_console_app_class):
        """Test that main function creates ConsoleApp with correct zip path."""
        mock_app = Mock()
        mock_console_app_class.return_value = mock_app
        
        main.main()
        
        # Verify ConsoleApp was created with Jan.zip
        mock_console_app_class.assert_called_once_with("Jan.zip")
        
        # Verify app.run() was called
        mock_app.run.assert_called_once()
        
    @patch('builtins.print')
    @patch('main.ConsoleApp')
    def test_main_prints_title(self, mock_console_app_class, mock_print):
        """Test that main function prints the application title."""
        mock_app = Mock()
        mock_console_app_class.return_value = mock_app
        
        main.main()
        
        # Check that title and separator were printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertIn("HTML Search Engine - Part 1", print_calls)
        self.assertIn("=" * 40, print_calls)


if __name__ == '__main__':
    unittest.main()