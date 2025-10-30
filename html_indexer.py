"""
HTML Indexer for Information Retrieval and Web Search Engine Project

This module provides the core functionality for extracting index terms from HTML files
contained in a zip archive and building efficient data structures for fast search operations.
"""

import re
import zipfile
import math
from collections import defaultdict, Counter
from typing import Dict, List, Set, Optional, NamedTuple, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class DocumentRecord(NamedTuple):
    """Record for document information in the document list."""
    doc_id: str
    url: str
    length: int  # Total number of words in document
    unique_words: int  # Number of unique words


class PostingRecord(NamedTuple):
    """Record for a posting in the inverted index."""
    doc_id: str
    term_frequency: int
    tf_idf: float
    positions: List[int]


class InvertedIndexEntry(NamedTuple):
    """Entry in the inverted index for a word."""
    word: str
    document_frequency: int
    postings: List[PostingRecord]


class HtmlIndexer:
    """
    Enhanced indexer for building inverted indices with TF-IDF calculations.

    This class processes HTML files from a zip archive and builds comprehensive
    data structures including:
    - Tokenizer with stop word removal and URL extraction
    - Document list with metadata
    - Inverted index with TF-IDF values and word positions
    - URL management for hyperlink tracking
    """
    
    def __init__(self, zip_path: str = "Jan.zip") -> None:
        """
        Initialize the HtmlIndexer with the specified zip file path.

        Args:
            zip_path: Path to the zip file containing HTML files (default: "Jan.zip")
        """
        self.zip_path: str = zip_path

        # Document ID management for collision handling
        self.used_ids: Set[str] = set()
        self.path_to_id: Dict[str, str] = {}  # original_path -> normalized_id
        self.id_to_path: Dict[str, str] = {}  # normalized_id -> original_path

        # Legacy data structures (kept for backward compatibility)
        self.file_words: Dict[str, Set[str]] = {}  # filename -> unique words
        self.word_files: Dict[str, List[str]] = defaultdict(list)  # word -> files containing it

        # New enhanced data structures
        self.document_list: Dict[str, DocumentRecord] = {}  # doc_id -> document record
        self.inverted_index: Dict[str, InvertedIndexEntry] = {}  # word -> inverted index entry
        self.url_list: List[str] = []  # List of extracted URLs
        self.url_status: Dict[str, str] = {}  # URL -> status (for future crawler)

        # Anchor text support (Part 3)
        self.anchor_texts: Dict[str, List[str]] = defaultdict(list)  # doc_id -> anchor texts pointing to it

        # Document statistics for TF-IDF calculation
        self.total_documents: int = 0
        self.avg_doc_length: float = 0.0

        # Configuration
        self.stop_words: Set[str] = self._get_default_stop_words()
        self.alphabetic_pattern: re.Pattern[str] = re.compile(r'^[a-zA-Z]+$')
        self.is_indexed: bool = False

    def _get_default_stop_words(self) -> Set[str]:
        """Return a set of common English stop words."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'this', 'but', 'or',
            'not', 'have', 'had', 'what', 'when', 'where', 'who', 'which',
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'can', 'may', 'should', 'would', 'could'
        }

    def set_stop_words(self, stop_words: Set[str]) -> None:
        """Set custom stop words list."""
        self.stop_words = stop_words

    def _normalize_path(self, path: str) -> str:
        """
        Normalize file path for consistent document IDs.

        Args:
            path: Original file path

        Returns:
            Normalized path string
        """
        from pathlib import Path

        # Convert to Path object for normalization
        normalized = str(Path(path).as_posix())

        # Ensure it starts with ./
        if not normalized.startswith('./'):
            normalized = './' + normalized.lstrip('./')

        return normalized

    def _generate_document_id(self, original_path: str) -> str:
        """
        Generate a unique document ID using filename + random number.

        Args:
            original_path: Original file path from zip

        Returns:
            Unique document ID in format: filename + random_number (e.g., "index9083")
        """
        # Check if we already have an ID for this path
        if original_path in self.path_to_id:
            return self.path_to_id[original_path]

        import random
        from pathlib import Path

        # Extract filename without extension
        filename = Path(original_path).stem  # e.g., "index" from "index.html"

        # Generate unique ID by trying random numbers
        max_attempts = 1000
        for _ in range(max_attempts):
            # Generate 4-digit random number
            random_num = random.randint(1000, 9999)
            doc_id = f"{filename}{random_num}"

            # Check if this ID is already used
            if doc_id not in self.used_ids:
                # Store mappings
                self.used_ids.add(doc_id)
                self.path_to_id[original_path] = doc_id
                self.id_to_path[doc_id] = original_path
                return doc_id

        # Fallback: if somehow we can't find a unique random number after 1000 attempts
        # (virtually impossible with 4-digit numbers), use a counter
        counter = 1
        while f"{filename}{counter:04d}" in self.used_ids:
            counter += 1

        doc_id = f"{filename}{counter:04d}"
        self.used_ids.add(doc_id)
        self.path_to_id[original_path] = doc_id
        self.id_to_path[doc_id] = original_path

        return doc_id

    def get_original_path(self, doc_id: str) -> Optional[str]:
        """
        Get original file path from document ID.

        Args:
            doc_id: Document ID

        Returns:
            Original file path or None if not found
        """
        return self.id_to_path.get(doc_id)
        
    def extract_urls_from_html(self, html_content: str, base_url: str = "") -> List[str]:
        """
        Extract all URLs from HTML content.

        Args:
            html_content: Raw HTML content as string
            base_url: Base URL for resolving relative links

        Returns:
            List of URLs found in the HTML content
        """
        soup = BeautifulSoup(html_content, 'lxml')
        urls = []

        # Extract URLs from various HTML elements
        for tag in soup.find_all(['a', 'link', 'img', 'script', 'iframe']):
            url = None
            if tag.name == 'a' and tag.get('href'):
                url = tag.get('href')
            elif tag.name == 'link' and tag.get('href'):
                url = tag.get('href')
            elif tag.name in ['img', 'script'] and tag.get('src'):
                url = tag.get('src')
            elif tag.name == 'iframe' and tag.get('src'):
                url = tag.get('src')

            if url:
                # Resolve relative URLs if base_url is provided
                if base_url and not url.startswith(('http://', 'https://', 'mailto:', 'javascript:')):
                    url = urljoin(base_url, url)
                urls.append(url)

        return urls

    def extract_words_with_positions(self, html_content: str) -> Tuple[List[str], Dict[str, List[int]]]:
        """
        Extract words with their positions from HTML content.

        Args:
            html_content: Raw HTML content as string

        Returns:
            Tuple of (word_list, position_dict) where:
            - word_list: List of all words in order
            - position_dict: Dict mapping words to their positions
        """
        soup = BeautifulSoup(html_content, 'lxml')

        # Extract all text content, removing HTML tags
        text = soup.get_text(separator=' ')

        # Split text into words and track positions
        words = []
        word_positions = defaultdict(list)
        position = 0

        for word in text.split():
            # Remove leading/trailing punctuation and convert to lowercase
            cleaned_word = word.strip('.,!?;:"()[]{}').lower()

            # Only include words that contain only alphabetic characters
            if cleaned_word and self.alphabetic_pattern.match(cleaned_word):
                # Skip stop words
                if cleaned_word not in self.stop_words:
                    words.append(cleaned_word)
                    word_positions[cleaned_word].append(position)
                    position += 1

        return words, dict(word_positions)

    def extract_words_with_positions_and_anchors(self, html_content: str, anchor_texts: List[str] = None) -> Tuple[List[str], Dict[str, List[int]]]:
        """
        Extract words with positions from HTML content, including anchor texts.

        Args:
            html_content: Raw HTML content as string
            anchor_texts: Optional list of anchor texts pointing to this document

        Returns:
            Tuple of (word_list, position_dict) where anchor texts are included
        """
        soup = BeautifulSoup(html_content, 'lxml')

        # Extract all text content, removing HTML tags
        text = soup.get_text(separator=' ')

        # Add anchor texts to the content (they get extra weight)
        if anchor_texts:
            # Add anchor texts 2 times for extra weight
            anchor_text_combined = ' '.join(anchor_texts)
            text = text + ' ' + anchor_text_combined + ' ' + anchor_text_combined

        # Split text into words and track positions
        words = []
        word_positions = defaultdict(list)
        position = 0

        for word in text.split():
            # Remove leading/trailing punctuation and convert to lowercase
            cleaned_word = word.strip('.,!?;:"()[]{}').lower()

            # Only include words that contain only alphabetic characters
            if cleaned_word and self.alphabetic_pattern.match(cleaned_word):
                # Skip stop words
                if cleaned_word not in self.stop_words:
                    words.append(cleaned_word)
                    word_positions[cleaned_word].append(position)
                    position += 1

        return words, dict(word_positions)

    def extract_anchor_texts_from_html(self, html_content: str) -> List[Tuple[str, str]]:
        """
        Extract anchor texts and their target URLs from HTML content.

        Args:
            html_content: Raw HTML content as string

        Returns:
            List of (url, anchor_text) tuples
        """
        soup = BeautifulSoup(html_content, 'lxml')
        anchor_data = []

        for tag in soup.find_all('a', href=True):
            href = tag.get('href', '')
            anchor_text = tag.get_text(strip=True)

            if href and anchor_text:
                anchor_data.append((href, anchor_text))

        return anchor_data

    def extract_words_from_html(self, html_content: str) -> Set[str]:
        """
        Extract alphabetic words from HTML content (legacy method).

        Args:
            html_content: Raw HTML content as string

        Returns:
            Set of lowercase alphabetic words found in the HTML content
        """
        words, _ = self.extract_words_with_positions(html_content)
        return set(words)
    
    def calculate_tf_idf(self, term_freq: int, doc_length: int, doc_freq: int) -> float:
        """
        Calculate TF-IDF value for a term.

        Args:
            term_freq: Frequency of term in document
            doc_length: Total words in document
            doc_freq: Number of documents containing the term

        Returns:
            TF-IDF value
        """
        if term_freq == 0 or doc_freq == 0:
            return 0.0

        # TF: term frequency / document length
        tf = term_freq / doc_length

        # IDF: log(total documents / document frequency)
        idf = math.log(self.total_documents / doc_freq) if doc_freq > 0 else 0.0

        return tf * idf

    def process_zip_file(self) -> None:
        """
        Process all HTML files in the zip archive and build enhanced index structures.

        Raises:
            FileNotFoundError: If the zip file is not found
            zipfile.BadZipFile: If the zip file is corrupted
        """
        if not Path(self.zip_path).exists():
            raise FileNotFoundError(f"Zip file '{self.zip_path}' not found")

        # First pass: collect document information
        document_word_counts = {}
        document_words_with_positions = {}
        all_document_urls = {}

        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith('.html'):
                    # Read HTML content from zip file
                    with zip_ref.open(file_info) as html_file:
                        html_content = html_file.read().decode('utf-8', errors='ignore')

                    # Generate unique document ID with collision handling
                    original_path = f"./{file_info.filename}"
                    doc_id = self._generate_document_id(original_path)

                    # Extract words with positions
                    words, word_positions = self.extract_words_with_positions(html_content)
                    document_words_with_positions[doc_id] = (words, word_positions)

                    # Extract URLs
                    urls = self.extract_urls_from_html(html_content)
                    all_document_urls[doc_id] = urls
                    self.url_list.extend(urls)

                    # Count word frequencies
                    word_counts = Counter(words)
                    document_word_counts[doc_id] = word_counts

                    # Create document record
                    self.document_list[doc_id] = DocumentRecord(
                        doc_id=doc_id,
                        url=file_info.filename,
                        length=len(words),
                        unique_words=len(set(words))
                    )

                    # Legacy compatibility
                    self.file_words[doc_id] = set(words)

        self.total_documents = len(self.document_list)
        if self.total_documents > 0:
            self.avg_doc_length = sum(doc.length for doc in self.document_list.values()) / self.total_documents

        # Remove duplicate URLs and initialize status
        self.url_list = list(set(self.url_list))
        for url in self.url_list:
            self.url_status[url] = "unvisited"  # For future crawler

        # Second pass: build inverted index with TF-IDF
        word_doc_frequencies = defaultdict(int)

        # Calculate document frequencies
        for doc_id, word_counts in document_word_counts.items():
            for word in word_counts.keys():
                word_doc_frequencies[word] += 1

        # Build inverted index
        for word, doc_freq in word_doc_frequencies.items():
            postings = []

            for doc_id, word_counts in document_word_counts.items():
                if word in word_counts:
                    term_freq = word_counts[word]
                    doc_length = self.document_list[doc_id].length
                    tf_idf = self.calculate_tf_idf(term_freq, doc_length, doc_freq)
                    positions = document_words_with_positions[doc_id][1][word]

                    posting = PostingRecord(
                        doc_id=doc_id,
                        term_frequency=term_freq,
                        tf_idf=tf_idf,
                        positions=positions
                    )
                    postings.append(posting)

            # Sort postings by TF-IDF score (descending)
            postings.sort(key=lambda p: p.tf_idf, reverse=True)

            self.inverted_index[word] = InvertedIndexEntry(
                word=word,
                document_frequency=doc_freq,
                postings=postings
            )

            # Legacy compatibility
            self.word_files[word] = [p.doc_id for p in postings]

        self.is_indexed = True

    def build_index_from_crawled_documents(self, documents: Dict[str, str], anchor_texts_map: Dict[str, List[str]] = None) -> None:
        """
        Build index from crawled documents (Part 3 - Spider integration).

        Args:
            documents: Dictionary mapping URLs to HTML content
            anchor_texts_map: Dictionary mapping URLs to their anchor texts
        """
        print("Building index from crawled documents...")
        print(f"Processing {len(documents)} documents")

        if anchor_texts_map is None:
            anchor_texts_map = {}

        # First pass: collect document information
        document_word_counts = {}
        document_words_with_positions = {}
        all_document_urls = {}

        for url, html_content in documents.items():
            # Generate unique document ID
            doc_id = self._generate_document_id(url)

            # Get anchor texts for this document
            anchors = anchor_texts_map.get(url, [])

            # Extract words with positions, including anchor texts
            words, word_positions = self.extract_words_with_positions_and_anchors(html_content, anchors)
            document_words_with_positions[doc_id] = (words, word_positions)

            # Store anchor texts
            if anchors:
                self.anchor_texts[doc_id] = anchors

            # Extract URLs from the document
            urls = self.extract_urls_from_html(html_content)
            all_document_urls[doc_id] = urls
            self.url_list.extend(urls)

            # Count word frequencies
            word_counts = Counter(words)
            document_word_counts[doc_id] = word_counts

            # Create document record
            self.document_list[doc_id] = DocumentRecord(
                doc_id=doc_id,
                url=url,
                length=len(words),
                unique_words=len(set(words))
            )

            # Legacy compatibility
            self.file_words[doc_id] = set(words)

        self.total_documents = len(self.document_list)
        if self.total_documents > 0:
            self.avg_doc_length = sum(doc.length for doc in self.document_list.values()) / self.total_documents

        # Remove duplicate URLs and initialize status
        self.url_list = list(set(self.url_list))
        for url in self.url_list:
            self.url_status[url] = "unvisited"

        # Second pass: build inverted index with TF-IDF
        word_doc_frequencies = defaultdict(int)

        # Calculate document frequencies
        for doc_id, word_counts in document_word_counts.items():
            for word in word_counts.keys():
                word_doc_frequencies[word] += 1

        # Build inverted index
        for word, doc_freq in word_doc_frequencies.items():
            postings = []

            for doc_id, word_counts in document_word_counts.items():
                if word in word_counts:
                    term_freq = word_counts[word]
                    doc_length = self.document_list[doc_id].length
                    tf_idf = self.calculate_tf_idf(term_freq, doc_length, doc_freq)
                    positions = document_words_with_positions[doc_id][1][word]

                    posting = PostingRecord(
                        doc_id=doc_id,
                        term_frequency=term_freq,
                        tf_idf=tf_idf,
                        positions=positions
                    )
                    postings.append(posting)

            # Sort postings by TF-IDF score (descending)
            postings.sort(key=lambda p: p.tf_idf, reverse=True)

            self.inverted_index[word] = InvertedIndexEntry(
                word=word,
                document_frequency=doc_freq,
                postings=postings
            )

            # Legacy compatibility
            self.word_files[word] = [p.doc_id for p in postings]

        self.is_indexed = True

        print(f"Successfully indexed {len(self.file_words)} documents")
        print(f"Built inverted index with {len(self.inverted_index)} unique words")
        print(f"Extracted {len(self.url_list)} unique URLs")
        print(f"Documents with anchor texts: {len(self.anchor_texts)}")
        print(f"Average document length: {self.avg_doc_length:.2f} words")

    def build_index(self) -> None:
        """
        Build the complete index from the zip file.

        This method processes all HTML files and creates the data structures
        needed for efficient search operations including inverted index with TF-IDF.
        """
        if not self.is_indexed:
            print("Processing HTML files...")
            self.process_zip_file()
            print(f"Successfully indexed {len(self.file_words)} HTML files")
            print(f"Built inverted index with {len(self.inverted_index)} unique words")
            print(f"Extracted {len(self.url_list)} unique URLs")
            print(f"Average document length: {self.avg_doc_length:.2f} words")
    
    def search_word(self, search_term: str) -> Optional[List[str]]:
        """
        Search for a term in the indexed files (legacy method).

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

    def search_word_with_scores(self, search_term: str) -> Optional[List[Tuple[str, float]]]:
        """
        Search for a term and return results with TF-IDF scores.

        Args:
            search_term: The word to search for (case-insensitive)

        Returns:
            List of (document_id, tf_idf_score) tuples, sorted by score descending
        """
        if not self.is_indexed:
            self.build_index()

        search_term_lower = search_term.lower().strip()
        entry = self.get_inverted_index_entry(search_term_lower)

        if entry:
            return [(posting.doc_id, posting.tf_idf) for posting in entry.postings]

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

    def get_inverted_index_entry(self, word: str) -> Optional[InvertedIndexEntry]:
        """
        Get the inverted index entry for a word.

        Args:
            word: Word to lookup

        Returns:
            InvertedIndexEntry if word exists, None otherwise
        """
        return self.inverted_index.get(word.lower())

    def get_document_record(self, doc_id: str) -> Optional[DocumentRecord]:
        """
        Get document record by document ID.

        Args:
            doc_id: Document identifier

        Returns:
            DocumentRecord if document exists, None otherwise
        """
        return self.document_list.get(doc_id)

    def get_all_urls(self) -> List[str]:
        """
        Get all extracted URLs.

        Returns:
            List of all URLs found in the documents
        """
        return self.url_list.copy()

    def get_url_status(self, url: str) -> Optional[str]:
        """
        Get the status of a URL (for future crawler use).

        Args:
            url: URL to check

        Returns:
            Status string if URL exists, None otherwise
        """
        return self.url_status.get(url)

    def set_url_status(self, url: str, status: str) -> None:
        """
        Set the status of a URL (for future crawler use).

        Args:
            url: URL to update
            status: New status (e.g., "visited", "unvisited", "error")
        """
        if url in self.url_status:
            self.url_status[url] = status