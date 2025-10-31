"""
Web Spider for Crawling HTML Documents
Information Retrieval and Web Search Engine Project - Part 3

This module implements a breadth-first web spider that crawls HTML documents
starting from an index.html file and collects all linked documents.

Optimized with parallel HTML parsing using ProcessPoolExecutor.
"""

import os
import zipfile
from collections import deque
from typing import Set, List, Dict, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count


# Worker functions for parallel processing (must be at module level for pickling)

def _read_html_from_zip(zip_path: str, file_path: str) -> Optional[str]:
    """
    Worker function to read HTML content from zip file.

    Args:
        zip_path: Path to zip file
        file_path: Path within zip

    Returns:
        HTML content or None if error
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if file_path in zip_ref.namelist():
                with zip_ref.open(file_path) as file:
                    return file.read().decode('utf-8', errors='ignore')

            # Try with path variations
            for name in zip_ref.namelist():
                normalized_name = name.replace('\\', '/').lstrip('/')
                normalized_path = file_path.replace('\\', '/').lstrip('/')
                if normalized_name == normalized_path:
                    with zip_ref.open(name) as file:
                        return file.read().decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None


def _extract_links_worker(args: Tuple[str, str, str]) -> Tuple[str, Optional[str], List[Tuple[str, str]]]:
    """
    Worker function to extract links and anchor texts from an HTML file.

    Args:
        args: Tuple of (zip_path, url, current_url)

    Returns:
        Tuple of (url, html_content, links_with_anchors)
    """
    zip_path, url, current_url = args

    # Read HTML content
    html_content = _read_html_from_zip(zip_path, url)

    if html_content is None:
        return (url, None, [])

    # Extract links and anchor texts
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        links_with_anchors = []

        for tag in soup.find_all('a', href=True):
            href = tag.get('href', '')
            anchor_text = tag.get_text(strip=True)

            # Normalize URL
            normalized_url = _normalize_url_worker(href, current_url)

            if normalized_url and _is_html_file_worker(normalized_url):
                links_with_anchors.append((normalized_url, anchor_text))

        return (url, html_content, links_with_anchors)
    except Exception:
        return (url, html_content, [])


def _normalize_url_worker(url: str, base_url: str = "") -> Optional[str]:
    """Worker function for URL normalization."""
    if not url:
        return None

    url = url.split('#')[0]

    if url.startswith(('mailto:', 'javascript:', 'tel:', 'ftp:')):
        return None

    if base_url:
        url = urljoin(base_url, url)

    url = unquote(url)
    url = url.lstrip('/')

    return url


def _is_html_file_worker(url: str) -> bool:
    """Worker function to check if URL is HTML."""
    lower_url = url.lower()
    return (lower_url.endswith('.html') or
            lower_url.endswith('.htm') or
            lower_url.endswith('/'))


def _parse_html_worker(args: Tuple[str, str, str]) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Worker function to parse HTML and extract links (for cached content).

    Args:
        args: Tuple of (url, html_content, current_url)

    Returns:
        Tuple of (url, links_with_anchors)
    """
    url, html_content, current_url = args

    try:
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, unquote

        soup = BeautifulSoup(html_content, 'lxml')
        links_with_anchors = []

        for tag in soup.find_all('a', href=True):
            href = tag.get('href', '')
            anchor_text = tag.get_text(strip=True)

            # Normalize URL
            normalized_url = _normalize_url_worker(href, current_url)

            if normalized_url and _is_html_file_worker(normalized_url):
                links_with_anchors.append((normalized_url, anchor_text))

        return (url, links_with_anchors)
    except Exception:
        return (url, [])


class WebSpider:
    """
    Breadth-First Web Spider for crawling HTML documents.

    This spider starts from an initial HTML file and uses breadth-first
    search to discover and collect all linked HTML documents within
    the same directory structure.
    """

    def __init__(self, zip_path: str = "rfh.zip", start_file: str = "rhf/index.html"):
        """
        Initialize the web spider.

        Args:
            zip_path: Path to the zip file containing HTML files
            start_file: Starting HTML file path within the zip
        """
        self.zip_path = zip_path
        self.start_file = start_file

        # Crawling state
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.url_queue: deque = deque()

        # Collected data
        self.html_documents: Dict[str, str] = {}  # url -> html_content
        self.anchor_texts: Dict[str, List[str]] = {}  # url -> list of anchor texts pointing to it
        self.url_graph: Dict[str, List[str]] = {}  # url -> list of outgoing links

        # Statistics
        self.pages_crawled = 0
        self.total_links_found = 0

    def _normalize_url(self, url: str, base_url: str = "") -> Optional[str]:
        """
        Normalize a URL for consistent comparison.

        Args:
            url: URL to normalize
            base_url: Base URL for resolving relative links

        Returns:
            Normalized URL string or None if invalid
        """
        if not url:
            return None

        # Remove fragments
        url = url.split('#')[0]

        # Skip non-HTML links
        if url.startswith(('mailto:', 'javascript:', 'tel:', 'ftp:')):
            return None

        # Resolve relative URLs
        if base_url:
            url = urljoin(base_url, url)

        # Decode URL-encoded characters
        url = unquote(url)

        # Normalize path separators for cross-platform compatibility
        # Remove leading slashes and normalize
        url = url.lstrip('/')

        return url

    def _is_html_file(self, url: str) -> bool:
        """
        Check if a URL points to an HTML file.

        Args:
            url: URL to check

        Returns:
            True if URL is an HTML file, False otherwise
        """
        # Check file extension
        lower_url = url.lower()
        return (lower_url.endswith('.html') or
                lower_url.endswith('.htm') or
                lower_url.endswith('/'))  # Directory index files

    def _extract_links_and_anchors(self, html_content: str, current_url: str) -> List[Tuple[str, str]]:
        """
        Extract all links and their anchor texts from HTML content.

        Args:
            html_content: Raw HTML content
            current_url: URL of the current page (for resolving relative links)

        Returns:
            List of (url, anchor_text) tuples
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links_with_anchors = []

        # Extract all anchor tags
        for tag in soup.find_all('a', href=True):
            href = tag.get('href', '')

            # Get anchor text (visible text in the link)
            anchor_text = tag.get_text(strip=True)

            # Normalize the URL
            normalized_url = self._normalize_url(href, current_url)

            if normalized_url and self._is_html_file(normalized_url):
                links_with_anchors.append((normalized_url, anchor_text))

        return links_with_anchors

    def _read_file_from_zip(self, file_path: str) -> Optional[str]:
        """
        Read a file from the zip archive.

        Args:
            file_path: Path to file within zip

        Returns:
            File content as string or None if not found
        """
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # Try exact match first
                if file_path in zip_ref.namelist():
                    with zip_ref.open(file_path) as file:
                        return file.read().decode('utf-8', errors='ignore')

                # Try with different path variations
                for name in zip_ref.namelist():
                    # Normalize both paths for comparison
                    normalized_name = name.replace('\\', '/').lstrip('/')
                    normalized_path = file_path.replace('\\', '/').lstrip('/')

                    if normalized_name == normalized_path:
                        with zip_ref.open(name) as file:
                            return file.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

        return None

    def _get_all_html_files_from_zip(self) -> List[str]:
        """
        Get all HTML files from the zip archive.

        Returns:
            List of HTML file paths
        """
        html_files = []
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                for file_info in zip_ref.namelist():
                    if file_info.endswith(('.html', '.htm')) and not file_info.startswith('__MACOSX'):
                        html_files.append(file_info)
        except Exception as e:
            print(f"Error reading zip file: {e}")

        return html_files

    def crawl_breadth_first(self, max_pages: Optional[int] = None, max_workers: Optional[int] = None) -> None:
        """
        Perform breadth-first crawling starting from the initial file.

        Uses chunked approach: Load all HTML from zip once, then process in parallel batches.

        Args:
            max_pages: Maximum number of pages to crawl (None for unlimited)
            max_workers: Number of worker processes (None = cpu_count(), use all cores)

        Note: Uses optimized chunked approach - loads zip once into memory,
              then processes HTML parsing in parallel. Best balance of speed + memory.
        """
        # Use chunked approach by default (best balance of speed + memory)
        if max_workers is None:
            max_workers = cpu_count()  # Use all cores for chunked processing

        # Use chunked streaming approach (optimal for zip files)
        self._crawl_breadth_first_chunked(max_pages, max_workers)

    def _crawl_breadth_first_sequential(self, max_pages: Optional[int] = None) -> None:
        """
        Sequential breadth-first crawling (original implementation).

        Args:
            max_pages: Maximum number of pages to crawl (None for unlimited)
        """
        print(f"Starting breadth-first crawl from {self.start_file}")
        print(f"Reading from {self.zip_path}")
        print("-" * 60)

        # Initialize queue with start file
        self.url_queue.append(self.start_file)
        self.discovered_urls.add(self.start_file)

        # Breadth-first search
        while self.url_queue and (max_pages is None or self.pages_crawled < max_pages):
            # Dequeue next URL
            current_url = self.url_queue.popleft()

            # Skip if already visited
            if current_url in self.visited_urls:
                continue

            # Mark as visited
            self.visited_urls.add(current_url)

            # Read HTML content
            html_content = self._read_file_from_zip(current_url)

            if html_content is None:
                print(f"⚠ Could not read: {current_url}")
                continue

            # Store HTML content
            self.html_documents[current_url] = html_content
            self.pages_crawled += 1

            print(f"✓ Crawled [{self.pages_crawled}]: {current_url}")

            # Extract links and anchor texts
            links_with_anchors = self._extract_links_and_anchors(html_content, current_url)

            # Store outgoing links
            outgoing_links = []

            for linked_url, anchor_text in links_with_anchors:
                self.total_links_found += 1
                outgoing_links.append(linked_url)

                # Store anchor text for the target URL
                if linked_url not in self.anchor_texts:
                    self.anchor_texts[linked_url] = []
                if anchor_text:  # Only store non-empty anchor texts
                    self.anchor_texts[linked_url].append(anchor_text)

                # Add to queue if not discovered yet
                if linked_url not in self.discovered_urls:
                    self.discovered_urls.add(linked_url)
                    self.url_queue.append(linked_url)

            self.url_graph[current_url] = outgoing_links

        print("-" * 60)
        print(f"Crawling completed!")
        print(f"Pages crawled: {self.pages_crawled}")
        print(f"Total links found: {self.total_links_found}")
        print(f"Unique URLs discovered: {len(self.discovered_urls)}")

    def _crawl_breadth_first_parallel(self, max_pages: Optional[int] = None, max_workers: int = None) -> None:
        """
        Parallel breadth-first crawling using ProcessPoolExecutor.

        Args:
            max_pages: Maximum number of pages to crawl (None for unlimited)
            max_workers: Number of worker processes
        """
        print(f"Starting parallel breadth-first crawl from {self.start_file}")
        print(f"Reading from {self.zip_path}")
        print(f"Using {max_workers} worker processes")
        print("-" * 60)

        # Initialize queue with start file
        self.url_queue.append(self.start_file)
        self.discovered_urls.add(self.start_file)

        # Batch size for parallel processing
        batch_size = max_workers * 4

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            while self.url_queue and (max_pages is None or self.pages_crawled < max_pages):
                # Collect batch of URLs to process
                batch = []
                while self.url_queue and len(batch) < batch_size:
                    if max_pages is not None and self.pages_crawled + len(batch) >= max_pages:
                        break

                    url = self.url_queue.popleft()

                    # Skip if already visited
                    if url in self.visited_urls:
                        continue

                    batch.append(url)
                    self.visited_urls.add(url)

                if not batch:
                    break

                # Process batch in parallel
                tasks = [(self.zip_path, url, url) for url in batch]
                futures = {executor.submit(_extract_links_worker, task): task[1] for task in tasks}

                # Collect results
                for future in as_completed(futures):
                    url = futures[future]

                    try:
                        result_url, html_content, links_with_anchors = future.result()

                        if html_content is None:
                            print(f"⚠ Could not read: {result_url}")
                            continue

                        # Store HTML content
                        self.html_documents[result_url] = html_content
                        self.pages_crawled += 1

                        print(f"✓ Crawled [{self.pages_crawled}]: {result_url}")

                        # Process links
                        outgoing_links = []
                        for linked_url, anchor_text in links_with_anchors:
                            self.total_links_found += 1
                            outgoing_links.append(linked_url)

                            # Store anchor text
                            if linked_url not in self.anchor_texts:
                                self.anchor_texts[linked_url] = []
                            if anchor_text:
                                self.anchor_texts[linked_url].append(anchor_text)

                            # Add to queue if not discovered
                            if linked_url not in self.discovered_urls:
                                self.discovered_urls.add(linked_url)
                                self.url_queue.append(linked_url)

                        self.url_graph[result_url] = outgoing_links

                    except Exception as e:
                        print(f"⚠ Error processing {url}: {e}")

        print("-" * 60)
        print(f"Crawling completed!")
        print(f"Pages crawled: {self.pages_crawled}")
        print(f"Total links found: {self.total_links_found}")
        print(f"Unique URLs discovered: {len(self.discovered_urls)}")

    def _crawl_breadth_first_chunked(self, max_pages: Optional[int] = None, max_workers: int = None) -> None:
        """
        Chunked breadth-first crawling with parallel processing.

        Strategy:
        1. Load all HTML files from zip into memory once (one sequential pass)
        2. Process BFS traversal using in-memory cache
        3. Parse HTML in parallel batches

        Args:
            max_pages: Maximum number of pages to crawl
            max_workers: Number of worker processes for parallel HTML parsing
        """
        print(f"Starting chunked breadth-first crawl from {self.start_file}")
        print(f"Reading from {self.zip_path}")
        print(f"Using {max_workers} workers for parallel parsing")
        print("-" * 60)

        # Step 1: Load ALL HTML files from zip into memory (one pass)
        print("Loading HTML files from zip...")
        html_cache = {}

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                html_files = [f for f in zip_ref.namelist()
                             if f.endswith(('.html', '.htm')) and not f.startswith('__MACOSX')]

                print(f"Found {len(html_files)} HTML files in zip")

                for file_path in html_files:
                    try:
                        with zip_ref.open(file_path) as file:
                            content = file.read().decode('utf-8', errors='ignore')
                            html_cache[file_path] = content
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Error reading zip: {e}")
            return

        print(f"✓ Loaded {len(html_cache)} files into memory")

        # Step 2: BFS traversal with parallel processing
        self.url_queue.append(self.start_file)
        self.discovered_urls.add(self.start_file)

        batch_size = max_workers * 4

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            while self.url_queue and (max_pages is None or self.pages_crawled < max_pages):
                # Collect batch of URLs
                batch = []
                while self.url_queue and len(batch) < batch_size:
                    if max_pages is not None and self.pages_crawled + len(batch) >= max_pages:
                        break

                    url = self.url_queue.popleft()

                    if url in self.visited_urls:
                        continue

                    # Check if we have this file in cache
                    if url not in html_cache:
                        continue

                    batch.append(url)
                    self.visited_urls.add(url)

                if not batch:
                    break

                # Process batch in parallel - parse HTML from cache
                tasks = []
                for url in batch:
                    html_content = html_cache[url]
                    tasks.append((url, html_content, url))

                # Submit to executor
                future_map = {executor.submit(_parse_html_worker, task): task[0] for task in tasks}

                # Collect results
                for future in as_completed(future_map):
                    url = future_map[future]

                    try:
                        result_url, links_with_anchors = future.result()
                        html_content = html_cache[result_url]

                        # Store HTML content
                        self.html_documents[result_url] = html_content
                        self.pages_crawled += 1

                        if self.pages_crawled % 100 == 0:
                            print(f"✓ Crawled [{self.pages_crawled}] pages...")

                        # Process links
                        outgoing_links = []
                        for linked_url, anchor_text in links_with_anchors:
                            self.total_links_found += 1
                            outgoing_links.append(linked_url)

                            # Store anchor text
                            if linked_url not in self.anchor_texts:
                                self.anchor_texts[linked_url] = []
                            if anchor_text:
                                self.anchor_texts[linked_url].append(anchor_text)

                            # Add to queue if not discovered
                            if linked_url not in self.discovered_urls:
                                self.discovered_urls.add(linked_url)
                                self.url_queue.append(linked_url)

                        self.url_graph[result_url] = outgoing_links

                    except Exception as e:
                        print(f"⚠ Error processing {url}: {e}")

        print("-" * 60)
        print(f"Crawling completed!")
        print(f"Pages crawled: {self.pages_crawled}")
        print(f"Total links found: {self.total_links_found}")
        print(f"Unique URLs discovered: {len(self.discovered_urls)}")

    def get_crawled_documents(self) -> Dict[str, str]:
        """
        Get all crawled HTML documents.

        Returns:
            Dictionary mapping URLs to HTML content
        """
        return self.html_documents.copy()

    def get_anchor_texts(self, url: str) -> List[str]:
        """
        Get all anchor texts pointing to a specific URL.

        Args:
            url: Target URL

        Returns:
            List of anchor texts
        """
        return self.anchor_texts.get(url, [])

    def get_all_anchor_texts(self) -> Dict[str, List[str]]:
        """
        Get all anchor texts for all URLs.

        Returns:
            Dictionary mapping URLs to their anchor texts
        """
        return self.anchor_texts.copy()

    def get_statistics(self) -> Dict[str, int]:
        """
        Get crawling statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            'pages_crawled': self.pages_crawled,
            'total_links_found': self.total_links_found,
            'unique_urls_discovered': len(self.discovered_urls),
            'urls_with_anchor_texts': len(self.anchor_texts)
        }

    def print_statistics(self) -> None:
        """Print detailed crawling statistics."""
        stats = self.get_statistics()
        print("\n" + "=" * 60)
        print("CRAWLING STATISTICS")
        print("=" * 60)
        print(f"Pages successfully crawled: {stats['pages_crawled']}")
        print(f"Total links found: {stats['total_links_found']}")
        print(f"Unique URLs discovered: {stats['unique_urls_discovered']}")
        print(f"URLs with anchor texts: {stats['urls_with_anchor_texts']}")

        if stats['pages_crawled'] > 0:
            avg_links = stats['total_links_found'] / stats['pages_crawled']
            print(f"Average links per page: {avg_links:.2f}")

        print("=" * 60)


def main():
    """Main function for testing the spider."""
    import sys

    # Check command line arguments
    zip_file = "rfh.zip" if len(sys.argv) < 2 else sys.argv[1]
    start_file = "rhf/index.html" if len(sys.argv) < 3 else sys.argv[2]

    # Create and run spider
    spider = WebSpider(zip_file, start_file)

    try:
        spider.crawl_breadth_first()
        spider.print_statistics()

        # Show sample anchor texts
        print("\nSample Anchor Texts (first 10):")
        print("-" * 60)
        for i, (url, anchors) in enumerate(list(spider.anchor_texts.items())[:10]):
            print(f"\n{url}")
            print(f"  Anchor texts: {anchors[:3]}")  # Show first 3 anchor texts

    except FileNotFoundError:
        print(f"Error: {zip_file} not found!")
        print("Please make sure the zip file exists in the current directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during crawling: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
