"""
Unit tests for HtmlIndexer class

Tests the core functionality of HTML parsing, word extraction, and indexing operations.
"""

import unittest
import tempfile
import zipfile
import os
from unittest.mock import patch, mock_open
from html_indexer import HtmlIndexer


class TestHtmlIndexer(unittest.TestCase):
    """Test cases for the HtmlIndexer class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.indexer = HtmlIndexer("test.zip")
        
    def tearDown(self):
        """Clean up after each test method."""
        pass
    
    def test_initialization(self):
        """Test proper initialization of HtmlIndexer."""
        self.assertEqual(self.indexer.zip_path, "test.zip")
        self.assertEqual(self.indexer.file_words, {})
        self.assertEqual(len(self.indexer.word_files), 0)
        self.assertFalse(self.indexer.is_indexed)
        
    def test_extract_words_from_html_basic(self):
        """Test basic word extraction from HTML content."""
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is a test paragraph with some words.</p>
            </body>
        </html>
        """
        
        words = self.indexer.extract_words_from_html(html_content)
        
        expected_words = {
            'hello', 'world', 'this', 'is', 'a', 'test', 'page',
            'paragraph', 'with', 'some', 'words'
        }
        
        self.assertTrue(expected_words.issubset(words))
        
    def test_extract_words_filters_non_alphabetic(self):
        """Test that non-alphabetic strings are filtered out."""
        html_content = """
        <html>
            <body>
                <p>Valid words: hello world</p>
                <p>Invalid: 123 hello123 $money @user #tag</p>
                <p>Mixed: can't don't it's</p>
                <script>var x = "code";</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """
        
        words = self.indexer.extract_words_from_html(html_content)
        
        # Should contain valid alphabetic words
        self.assertIn('hello', words)
        self.assertIn('world', words)
        self.assertIn('valid', words)
        self.assertIn('words', words)
        self.assertIn('invalid', words)
        self.assertIn('mixed', words)
        # Note: contractions like can't, don't are split by punctuation
        # so 'can', 'don', 'it' may not be extracted as standalone words
        
        # Should NOT contain non-alphabetic strings
        self.assertNotIn('123', words)
        self.assertNotIn('hello123', words)
        self.assertNotIn('$money', words)
        self.assertNotIn('@user', words)
        self.assertNotIn('#tag', words)
        self.assertNotIn("can't", words)
        self.assertNotIn("don't", words)
        self.assertNotIn("it's", words)
        
    def test_extract_words_case_conversion(self):
        """Test that all words are converted to lowercase."""
        html_content = """
        <html>
            <body>
                <h1>UPPERCASE</h1>
                <p>MixedCase</p>
                <p>lowercase</p>
            </body>
        </html>
        """
        
        words = self.indexer.extract_words_from_html(html_content)
        
        self.assertIn('uppercase', words)
        self.assertIn('mixedcase', words)
        self.assertIn('lowercase', words)
        
        # Should not contain uppercase versions
        self.assertNotIn('UPPERCASE', words)
        self.assertNotIn('MixedCase', words)
        
    def test_extract_words_ignores_html_tags(self):
        """Test that HTML tags and attributes are ignored."""
        html_content = """
        <html>
            <head>
                <title>Test Title</title>
                <style type="text/css">
                    body { background-color: white; }
                </style>
            </head>
            <body bgcolor="#ffffff" text="#000000">
                <div class="content" id="main">
                    <a href="http://example.com" target="_blank">Link</a>
                </div>
            </body>
        </html>
        """
        
        words = self.indexer.extract_words_from_html(html_content)
        
        # Should contain text content (words from visible text and CSS content)
        self.assertIn('test', words)
        self.assertIn('title', words)
        self.assertIn('link', words)
        # Note: CSS content like 'body', 'background-color', 'white' might be parsed differently
        
        # Should NOT contain HTML attributes
        self.assertNotIn('bgcolor', words)
        self.assertNotIn('#ffffff', words)
        self.assertNotIn('#000000', words)
        self.assertNotIn('http://example.com', words)
        self.assertNotIn('target', words)
        self.assertNotIn('_blank', words)
        
    def test_search_word_before_indexing(self):
        """Test that search_word triggers indexing if not already done."""
        with patch.object(self.indexer, 'build_index') as mock_build:
            self.indexer.search_word('test')
            mock_build.assert_called_once()
            
    def test_search_word_case_insensitive(self):
        """Test that search is case-insensitive."""
        # Mock the word_files dictionary
        self.indexer.word_files = {'hello': ['file1.html'], 'world': ['file2.html']}
        self.indexer.is_indexed = True
        
        # Test different cases
        self.assertEqual(self.indexer.search_word('hello'), ['file1.html'])
        self.assertEqual(self.indexer.search_word('HELLO'), ['file1.html'])
        self.assertEqual(self.indexer.search_word('Hello'), ['file1.html'])
        self.assertEqual(self.indexer.search_word('HeLLo'), ['file1.html'])
        
    def test_search_word_not_found(self):
        """Test search for non-existent word returns None."""
        self.indexer.word_files = {'hello': ['file1.html']}
        self.indexer.is_indexed = True
        
        result = self.indexer.search_word('notfound')
        self.assertIsNone(result)
        
    def test_search_word_whitespace_handling(self):
        """Test that search handles whitespace correctly."""
        self.indexer.word_files = {'hello': ['file1.html']}
        self.indexer.is_indexed = True
        
        # Test with whitespace
        self.assertEqual(self.indexer.search_word('  hello  '), ['file1.html'])
        self.assertEqual(self.indexer.search_word('\thello\n'), ['file1.html'])
        
    def test_get_file_count(self):
        """Test getting the count of indexed files."""
        self.indexer.file_words = {
            'file1.html': {'word1', 'word2'},
            'file2.html': {'word3', 'word4'},
            'file3.html': {'word5'}
        }
        
        self.assertEqual(self.indexer.get_file_count(), 3)
        
    def test_get_vocabulary_size(self):
        """Test getting the total vocabulary size."""
        self.indexer.word_files = {
            'word1': ['file1.html'],
            'word2': ['file1.html', 'file2.html'],
            'word3': ['file2.html'],
            'word4': ['file3.html']
        }
        
        self.assertEqual(self.indexer.get_vocabulary_size(), 4)
        
    def test_get_words_in_file(self):
        """Test retrieving words for a specific file."""
        test_words = {'hello', 'world', 'test'}
        self.indexer.file_words = {'file1.html': test_words}
        
        result = self.indexer.get_words_in_file('file1.html')
        self.assertEqual(result, test_words)
        
        # Test non-existent file
        result = self.indexer.get_words_in_file('nonexistent.html')
        self.assertIsNone(result)
        
    def create_test_zip(self, files_content):
        """Helper method to create a temporary zip file for testing."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(temp_file.name, 'w') as zip_file:
            for filename, content in files_content.items():
                zip_file.writestr(filename, content)
        return temp_file.name
        
    def test_process_zip_file_success(self):
        """Test successful processing of zip file."""
        test_files = {
            'Jan/test1.html': '<html><body>hello world</body></html>',
            'Jan/test2.html': '<html><body>goodbye universe</body></html>'
        }
        
        zip_path = self.create_test_zip(test_files)
        
        try:
            indexer = HtmlIndexer(zip_path)
            indexer.process_zip_file()
            
            self.assertTrue(indexer.is_indexed)
            self.assertEqual(len(indexer.file_words), 2)
            self.assertIn('./Jan/test1.html', indexer.file_words)
            self.assertIn('./Jan/test2.html', indexer.file_words)
            
            # Check words were extracted
            self.assertIn('hello', indexer.word_files)
            self.assertIn('world', indexer.word_files)
            self.assertIn('goodbye', indexer.word_files)
            self.assertIn('universe', indexer.word_files)
            
        finally:
            os.unlink(zip_path)
            
    def test_process_zip_file_not_found(self):
        """Test handling of non-existent zip file."""
        indexer = HtmlIndexer("nonexistent.zip")
        
        with self.assertRaises(FileNotFoundError):
            indexer.process_zip_file()
            
    def test_build_index_only_once(self):
        """Test that build_index only processes files once."""
        test_files = {
            'Jan/test.html': '<html><body>test</body></html>'
        }
        
        zip_path = self.create_test_zip(test_files)
        
        try:
            indexer = HtmlIndexer(zip_path)
            
            # First call should process files
            with patch.object(indexer, 'process_zip_file', wraps=indexer.process_zip_file) as mock_process:
                indexer.build_index()
                mock_process.assert_called_once()
                
            # Verify indexer is marked as indexed
            self.assertTrue(indexer.is_indexed)
            
            # Second call should not process files again (already indexed)
            with patch.object(indexer, 'process_zip_file') as mock_process:
                indexer.build_index()
                mock_process.assert_not_called()
                
        finally:
            os.unlink(zip_path)


if __name__ == '__main__':
    unittest.main()