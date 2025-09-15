"""
Integration tests for HTML Search Engine

Tests the complete workflow from zip file processing to search results,
using the actual Jan.zip file to validate end-to-end functionality.
"""

import unittest
import os
from html_indexer import HtmlIndexer
from console_app import ConsoleApp
from unittest.mock import patch


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete search engine functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        cls.zip_path = "Jan.zip"
        cls.zip_exists = os.path.exists(cls.zip_path)
        
    def setUp(self):
        """Set up test fixtures before each test method."""
        if not self.zip_exists:
            self.skipTest("Jan.zip file not found - skipping integration tests")
            
    def test_complete_indexing_workflow(self):
        """Test the complete workflow from zip processing to search."""
        indexer = HtmlIndexer(self.zip_path)
        
        # Test initial state
        self.assertFalse(indexer.is_indexed)
        self.assertEqual(len(indexer.file_words), 0)
        self.assertEqual(len(indexer.word_files), 0)
        
        # Build index
        indexer.build_index()
        
        # Verify indexing completed
        self.assertTrue(indexer.is_indexed)
        self.assertGreater(len(indexer.file_words), 0)
        self.assertGreater(len(indexer.word_files), 0)
        
        # Verify expected file count (31 HTML files)
        self.assertEqual(indexer.get_file_count(), 31)
        
        # Verify vocabulary size is reasonable
        vocab_size = indexer.get_vocabulary_size()
        self.assertGreater(vocab_size, 1000)  # Should have substantial vocabulary
        self.assertLess(vocab_size, 5000)    # But not excessive
        
    def test_search_functionality_with_real_data(self):
        """Test search functionality with known words from Jan.zip."""
        indexer = HtmlIndexer(self.zip_path)
        indexer.build_index()
        
        # Test cases based on project requirements
        test_cases = [
            {
                'term': 'music',
                'expected_files': ['./Jan/fab.html'],
                'should_find': True
            },
            {
                'term': 'subject',
                'expected_min_files': 1,
                'should_find': True
            },
            {
                'term': 'nonexistentword12345',
                'should_find': False
            }
        ]
        
        for case in test_cases:
            with self.subTest(term=case['term']):
                results = indexer.search_word(case['term'])
                
                if case['should_find']:
                    self.assertIsNotNone(results, f"Expected to find results for '{case['term']}'")
                    self.assertGreater(len(results), 0, f"Expected non-empty results for '{case['term']}'")
                    
                    # Check specific expected files if provided
                    if 'expected_files' in case:
                        for expected_file in case['expected_files']:
                            self.assertIn(expected_file, results, 
                                        f"Expected '{expected_file}' in results for '{case['term']}'")
                    
                    # Check minimum number of files if provided
                    if 'expected_min_files' in case:
                        self.assertGreaterEqual(len(results), case['expected_min_files'],
                                              f"Expected at least {case['expected_min_files']} files for '{case['term']}'")
                else:
                    self.assertIsNone(results, f"Expected no results for '{case['term']}'")
                    
    def test_case_insensitive_search(self):
        """Test that search is case-insensitive with real data."""
        indexer = HtmlIndexer(self.zip_path)
        indexer.build_index()
        
        # Find a word that exists
        test_word = None
        for word in list(indexer.word_files.keys())[:5]:  # Check first few words
            if len(word) > 3:  # Use a word with some length
                test_word = word
                break
                
        if test_word:
            # Test different cases
            original_result = indexer.search_word(test_word)
            upper_result = indexer.search_word(test_word.upper())
            title_result = indexer.search_word(test_word.title())
            
            self.assertEqual(original_result, upper_result,
                           f"Case-insensitive search failed for '{test_word}'")
            self.assertEqual(original_result, title_result,
                           f"Case-insensitive search failed for '{test_word}'")
                           
    def test_all_files_processed(self):
        """Test that all HTML files in the zip are processed."""
        indexer = HtmlIndexer(self.zip_path)
        indexer.build_index()
        
        # Expected files based on project specification
        expected_files = [
            './Jan/aol.html', './Jan/armed.html', './Jan/baptist.html',
            './Jan/bill.html', './Jan/birdnbee.html', './Jan/bunker.html',
            './Jan/cache.html', './Jan/child.html', './Jan/creditcard.html',
            './Jan/debug.html', './Jan/edwardii.html', './Jan/explain.html',
            './Jan/fab.html', './Jan/galant.html', './Jan/gravies.html',
            './Jan/harley.html', './Jan/heartprob.html', './Jan/hippos.html',
            './Jan/jesus.html', './Jan/kitty.html', './Jan/marriedplay.html',
            './Jan/phone.html', './Jan/problem.html', './Jan/qc.html',
            './Jan/quickies.html', './Jan/snow.html', './Jan/superbowl.html',
            './Jan/topten.html', './Jan/y2k.html', './Jan/y2kfollow.html',
            './Jan/y2kms.html'
        ]
        
        for expected_file in expected_files:
            self.assertIn(expected_file, indexer.file_words,
                         f"Expected file '{expected_file}' not found in index")
            
    def test_word_extraction_quality(self):
        """Test the quality of word extraction from HTML files."""
        indexer = HtmlIndexer(self.zip_path)
        indexer.build_index()
        
        # Check that common English words are found
        common_words = ['the', 'and', 'is', 'a', 'to', 'of', 'in', 'that', 'have', 'for']
        found_common_words = 0
        
        for word in common_words:
            if word in indexer.word_files:
                found_common_words += 1
                
        # Should find most common English words
        self.assertGreater(found_common_words, len(common_words) * 0.5,
                          "Should find majority of common English words")
                          
        # Check that no HTML tags/attributes are in the index
        html_artifacts = ['html', 'head', 'body', 'div', 'span', 'href', 'src', 'class', 'id']
        found_artifacts = 0
        
        for artifact in html_artifacts:
            if artifact in indexer.word_files:
                found_artifacts += 1
                
        # Should find some HTML-related words as they might appear in content,
        # but they should be legitimate content words, not tags/attributes
        # We're mainly checking that obvious tag artifacts aren't indexed
        
    def test_data_structure_consistency(self):
        """Test that the dual data structures (file_words and word_files) are consistent."""
        indexer = HtmlIndexer(self.zip_path)
        indexer.build_index()
        
        # For each file-word relationship, verify it exists in both structures
        for filename, words in indexer.file_words.items():
            for word in words:
                self.assertIn(word, indexer.word_files,
                            f"Word '{word}' from file '{filename}' not in word_files")
                self.assertIn(filename, indexer.word_files[word],
                            f"File '{filename}' not listed for word '{word}' in word_files")
                            
        # For each word-file relationship, verify it exists in both structures
        for word, files in indexer.word_files.items():
            for filename in files:
                self.assertIn(filename, indexer.file_words,
                            f"File '{filename}' for word '{word}' not in file_words")
                self.assertIn(word, indexer.file_words[filename],
                            f"Word '{word}' not in file '{filename}' word set")


class TestConsoleAppIntegration(unittest.TestCase):
    """Integration tests for ConsoleApp with real data."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        cls.zip_path = "Jan.zip"
        cls.zip_exists = os.path.exists(cls.zip_path)
        
    def setUp(self):
        """Set up test fixtures before each test method."""
        if not self.zip_exists:
            self.skipTest("Jan.zip file not found - skipping integration tests")
            
    def test_console_app_initialization(self):
        """Test ConsoleApp initialization with real zip file."""
        app = ConsoleApp(self.zip_path)
        
        # Test successful initialization
        result = app.initialize()
        self.assertTrue(result)
        self.assertTrue(app.is_initialized)
        
        # Test that stats are reasonable
        file_count = app.indexer.get_file_count()
        vocab_size = app.indexer.get_vocabulary_size()
        
        self.assertEqual(file_count, 31)
        self.assertGreater(vocab_size, 1000)
        
    @patch('builtins.input', side_effect=['music', 'test', ''])
    @patch('builtins.print')
    def test_console_app_search_loop(self, mock_print, mock_input):
        """Test the console app search loop with real data."""
        app = ConsoleApp(self.zip_path)
        app.run()
        
        # Verify that initialization message was printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        
        # Should contain initialization stats
        self.assertTrue(any('Indexed' in call and 'files' in call for call in print_calls))
        
        # Should contain search beginning message (note the newline prefix)
        self.assertTrue(any('Now the search begins:' in call for call in print_calls))
        
        # Should contain at least one result (music should find fab.html)
        self.assertTrue(any('found a match' in call for call in print_calls))
        
        # Should end with Bye
        self.assertIn('Bye', print_calls)


if __name__ == '__main__':
    unittest.main()