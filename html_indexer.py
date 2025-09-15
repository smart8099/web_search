"""
HTML Indexer for Information Retrieval and Web Search Engine Project

This module provides the core functionality for extracting index terms from HTML files
contained in a zip archive and building efficient data structures for fast search operations.
"""

import re
import zipfile
from collections import defaultdict
from typing import Dict, List, Set, Optional
from pathlib import Path
from bs4 import BeautifulSoup


class HtmlIndexer:
    """
    A class for indexing HTML files and extracting alphabetic terms for search operations.
    
    This class processes HTML files from a zip archive, extracts only alphabetic words,
    converts them to lowercase, and builds efficient data structures for O(1) search lookups.
    """
    
    def __init__(self, zip_path: str = "Jan.zip") -> None:
        """
        Initialize the HtmlIndexer with the specified zip file path.
        
        Args:
            zip_path: Path to the zip file containing HTML files (default: "Jan.zip")
        """
        self.zip_path: str = zip_path
        self.file_words: Dict[str, Set[str]] = {}  # filename -> unique words
        self.word_files: Dict[str, List[str]] = defaultdict(list)  # word -> files containing it
        self.alphabetic_pattern: re.Pattern[str] = re.compile(r'^[a-zA-Z]+$')
        self.is_indexed: bool = False
        
    def extract_words_from_html(self, html_content: str) -> Set[str]:
        """
        Extract alphabetic words from HTML content.
        
        Args:
            html_content: Raw HTML content as string
            
        Returns:
            Set of lowercase alphabetic words found in the HTML content
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract all text content, removing HTML tags
        text = soup.get_text(separator=' ')
        
        # Split text into words and filter for alphabetic-only words
        words = set()
        for word in text.split():
            # Remove leading/trailing punctuation and convert to lowercase
            cleaned_word = word.strip('.,!?;:"()[]{}').lower()
            
            # Only include words that contain only alphabetic characters
            if cleaned_word and self.alphabetic_pattern.match(cleaned_word):
                words.add(cleaned_word)
                
        return words
    
    def process_zip_file(self) -> None:
        """
        Process all HTML files in the zip archive and build index structures.
        
        Raises:
            FileNotFoundError: If the zip file is not found
            zipfile.BadZipFile: If the zip file is corrupted
        """
        if not Path(self.zip_path).exists():
            raise FileNotFoundError(f"Zip file '{self.zip_path}' not found")
            
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith('.html'):
                    # Read HTML content from zip file
                    with zip_ref.open(file_info) as html_file:
                        html_content = html_file.read().decode('utf-8', errors='ignore')
                    
                    # Extract words from HTML content
                    words = self.extract_words_from_html(html_content)
                    
                    # Store words for this file
                    filename = f"./{file_info.filename}"
                    self.file_words[filename] = words
                    
                    # Build reverse index for fast search
                    for word in words:
                        if filename not in self.word_files[word]:
                            self.word_files[word].append(filename)

        
         
        self.is_indexed = True
        
    def build_index(self) -> None:
        """
        Build the complete index from the zip file.
        
        This method processes all HTML files and creates the data structures
        needed for efficient search operations.
        """
        if not self.is_indexed:
            print("Processing HTML files...")
            self.process_zip_file()
            print(f"Successfully indexed {len(self.file_words)} HTML files")
    
    def search_word(self, search_term: str) -> Optional[List[str]]:
        """
        Search for a term in the indexed files.
        
        Args:
            search_term: The word to search for (case-insensitive)
            
        Returns:
            List of filenames containing the search term, or None if not found
        """
        if not self.is_indexed:
            self.build_index()
            
        search_term_lower = search_term.lower().strip()
        
        if search_term_lower in self.word_files:
            return self.word_files[search_term_lower]
        
        return None
    
    def get_file_count(self) -> int:
        """
        Get the total number of indexed files.
        
        Returns:
            Number of files that have been indexed
        """
        return len(self.file_words)
    
    def get_vocabulary_size(self) -> int:
        """
        Get the total number of unique words in the vocabulary.
        
        Returns:
            Total number of unique words across all files
        """
        return len(self.word_files)
    
    def get_words_in_file(self, filename: str) -> Optional[Set[str]]:
        """
        Get all words contained in a specific file.
        
        Args:
            filename: Name of the file to retrieve words for
            
        Returns:
            Set of words in the file, or None if file not found
        """
        return self.file_words.get(filename)