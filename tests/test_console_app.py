"""
Unit tests for ConsoleApp class

Tests the console interface functionality including initialization, user input handling,
and search result display.
"""

import unittest
from unittest.mock import Mock, patch, call
from io import StringIO
import sys
from console_app import ConsoleApp
from html_indexer import HtmlIndexer


class TestConsoleApp(unittest.TestCase):
    """Test cases for the ConsoleApp class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = ConsoleApp("test.zip")
        
    def tearDown(self):
        """Clean up after each test method."""
        pass
        
    def test_initialization(self):
        """Test proper initialization of ConsoleApp."""
        self.assertEqual(self.app.indexer.zip_path, "test.zip")
        self.assertFalse(self.app.is_initialized)
        
    @patch('console_app.HtmlIndexer')
    def test_initialize_success(self, mock_indexer_class):
        """Test successful initialization."""
        mock_indexer = Mock()
        mock_indexer_class.return_value = mock_indexer
        
        app = ConsoleApp("test.zip")
        result = app.initialize()
        
        self.assertTrue(result)
        self.assertTrue(app.is_initialized)
        mock_indexer.build_index.assert_called_once()
        
    @patch('console_app.HtmlIndexer')
    def test_initialize_failure_file_not_found(self, mock_indexer_class):
        """Test initialization failure when zip file not found."""
        mock_indexer = Mock()
        mock_indexer.build_index.side_effect = FileNotFoundError("File not found")
        mock_indexer_class.return_value = mock_indexer
        
        app = ConsoleApp("nonexistent.zip")
        
        with patch('builtins.print') as mock_print:
            result = app.initialize()
            
        self.assertFalse(result)
        self.assertFalse(app.is_initialized)
        mock_print.assert_called_with("Error initializing indexer: File not found")
        
    @patch('console_app.HtmlIndexer')
    def test_initialize_failure_generic_exception(self, mock_indexer_class):
        """Test initialization failure with generic exception."""
        mock_indexer = Mock()
        mock_indexer.build_index.side_effect = Exception("Generic error")
        mock_indexer_class.return_value = mock_indexer
        
        app = ConsoleApp("test.zip")
        
        with patch('builtins.print') as mock_print:
            result = app.initialize()
            
        self.assertFalse(result)
        self.assertFalse(app.is_initialized)
        mock_print.assert_called_with("Error initializing indexer: Generic error")
        
    def test_display_stats(self):
        """Test display of indexing statistics."""
        # Test when initialized
        self.app.is_initialized = True
        self.app.indexer.get_file_count = Mock(return_value=31)
        self.app.indexer.get_vocabulary_size = Mock(return_value=1855)
        
        with patch('builtins.print') as mock_print:
            self.app.display_stats()
            
        mock_print.assert_called_with("Indexed 31 files with 1855 unique words")
        
        # Test when not initialized
        self.app.is_initialized = False
        
        with patch('builtins.print') as mock_print:
            self.app.display_stats()
            
        # Should not print anything when not initialized
        mock_print.assert_not_called()
        
    def test_search_and_display_not_initialized(self):
        """Test search when app is not initialized."""
        self.app.is_initialized = False
        
        with patch('builtins.print') as mock_print:
            self.app.search_and_display("test")
            
        mock_print.assert_called_with("Error: Indexer not initialized")
        
    def test_search_and_display_empty_term(self):
        """Test search with empty search term."""
        self.app.is_initialized = True
        
        with patch('builtins.print') as mock_print:
            self.app.search_and_display("")
            self.app.search_and_display("   ")
            
        # Should not print anything for empty terms
        mock_print.assert_not_called()
        
    def test_search_and_display_found_single_result(self):
        """Test search with single result found."""
        self.app.is_initialized = True
        self.app.indexer.search_word = Mock(return_value=["./Jan/fab.html"])
        
        with patch('builtins.print') as mock_print:
            self.app.search_and_display("music")
            
        mock_print.assert_called_with("found a match: ./Jan/fab.html")
        
    def test_search_and_display_found_multiple_results(self):
        """Test search with multiple results found."""
        self.app.is_initialized = True
        self.app.indexer.search_word = Mock(return_value=["./Jan/fab.html", "./Jan/hippos.html"])
        
        with patch('builtins.print') as mock_print:
            self.app.search_and_display("music")
            
        mock_print.assert_called_with("found a match: ./Jan/fab.html ./Jan/hippos.html")
        
    def test_search_and_display_no_match(self):
        """Test search with no results found."""
        self.app.is_initialized = True
        self.app.indexer.search_word = Mock(return_value=None)
        
        with patch('builtins.print') as mock_print:
            self.app.search_and_display("nonexistent")
            
        mock_print.assert_called_with("no match")
        
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_initialization_failure(self, mock_print, mock_input):
        """Test run method when initialization fails."""
        with patch.object(self.app, 'initialize', return_value=False):
            self.app.run()
            
        mock_print.assert_called_with("Failed to initialize the search engine. Please check that Jan.zip exists.")
        
    @patch('builtins.input', side_effect=["music", "cat", ""])
    @patch('builtins.print')
    def test_run_successful_search_loop(self, mock_print, mock_input):
        """Test successful execution of search loop."""
        # Mock successful initialization
        with patch.object(self.app, 'initialize', return_value=True):
            self.app.is_initialized = True
            self.app.indexer.get_file_count = Mock(return_value=31)
            self.app.indexer.get_vocabulary_size = Mock(return_value=1855)
            
            # Mock search results
            def mock_search(term):
                if term == "music":
                    return ["./Jan/fab.html"]
                elif term == "cat":
                    return None
                return None
                    
            self.app.indexer.search_word = Mock(side_effect=mock_search)
            
            self.app.run()
            
        # Check all expected print calls
        expected_calls = [
            call("Indexed 31 files with 1855 unique words"),
            call("\nNow the search begins:"),
            call("found a match: ./Jan/fab.html"),
            call("no match"),
            call("Bye")
        ]
        
        mock_print.assert_has_calls(expected_calls, any_order=False)
        
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        """Test handling of keyboard interrupt during search loop."""
        with patch.object(self.app, 'initialize', return_value=True):
            self.app.is_initialized = True
            self.app.indexer.get_file_count = Mock(return_value=31)
            self.app.indexer.get_vocabulary_size = Mock(return_value=1855)
            
            self.app.run()
            
        # Should print newline and Bye
        calls = mock_print.call_args_list
        self.assertIn(call("\n"), calls)
        self.assertIn(call("Bye"), calls)
        
    @patch('builtins.input', side_effect=EOFError())
    @patch('builtins.print')
    def test_run_eof_error(self, mock_print, mock_input):
        """Test handling of EOF error during search loop."""
        with patch.object(self.app, 'initialize', return_value=True):
            self.app.is_initialized = True
            self.app.indexer.get_file_count = Mock(return_value=31)
            self.app.indexer.get_vocabulary_size = Mock(return_value=1855)
            
            self.app.run()
            
        # Should still print Bye
        self.assertIn(call("Bye"), mock_print.call_args_list)
        
    @patch('builtins.input', side_effect=["test", "hello", ""])
    @patch('builtins.print')
    def test_run_case_sensitivity(self, mock_print, mock_input):
        """Test that search terms are passed correctly to indexer."""
        with patch.object(self.app, 'initialize', return_value=True):
            self.app.is_initialized = True
            self.app.indexer.get_file_count = Mock(return_value=10)
            self.app.indexer.get_vocabulary_size = Mock(return_value=100)
            self.app.indexer.search_word = Mock(return_value=None)
            
            self.app.run()
            
        # Verify search_word was called with correct terms
        expected_calls = [call("test"), call("hello")]
        self.app.indexer.search_word.assert_has_calls(expected_calls)
        
    @patch('builtins.input', side_effect=["  test  ", ""])
    @patch('builtins.print')
    def test_run_whitespace_handling(self, mock_print, mock_input):
        """Test that whitespace in search terms is handled properly."""
        with patch.object(self.app, 'initialize', return_value=True):
            self.app.is_initialized = True
            self.app.indexer.get_file_count = Mock(return_value=10)
            self.app.indexer.get_vocabulary_size = Mock(return_value=100)
            self.app.indexer.search_word = Mock(return_value=None)
            
            self.app.run()
            
        # Search word should be called with the original term (indexer handles whitespace)
        self.app.indexer.search_word.assert_called_with("  test  ")


class TestConsoleAppMain(unittest.TestCase):
    """Test cases for the main function in console_app."""
    
    @patch('console_app.ConsoleApp')
    def test_main_function(self, mock_console_app_class):
        """Test the main function creates and runs ConsoleApp."""
        mock_app = Mock()
        mock_console_app_class.return_value = mock_app
        
        from console_app import main
        main()
        
        mock_console_app_class.assert_called_once()
        mock_app.run.assert_called_once()


if __name__ == '__main__':
    unittest.main()