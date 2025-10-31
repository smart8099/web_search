#!/usr/bin/env python3
"""
Main Application for Part 3: Spidering and Indexing the Entire Corpus

This integrates the web spider and indexer to crawl and index the rfh.zip corpus.
Uses breadth-first search strategy for crawling.

Information Retrieval and Web Search Engine Project - Part 3
"""

import sys
from pathlib import Path
from web_spider import WebSpider
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor


class Part3Application:
    """
    Main application for Part 3 that integrates spidering and indexing.
    """

    def __init__(self, zip_path: str = "rfh.zip", start_file: str = "rhf/index.html"):
        """
        Initialize Part 3 application.

        Args:
            zip_path: Path to the corpus zip file
            start_file: Starting HTML file for the spider
        """
        self.zip_path = zip_path
        self.start_file = start_file

        self.spider = None
        self.indexer = None
        self.query_processor = None

    def run_spider(self, max_pages: int = None) -> None:
        """
        Run the web spider to crawl documents.

        Args:
            max_pages: Maximum pages to crawl (None for all)
        """
        print("=" * 70)
        print("STEP 1: WEB SPIDERING")
        print("=" * 70)

        self.spider = WebSpider(self.zip_path, self.start_file)
        self.spider.crawl_breadth_first(max_pages=max_pages)
        self.spider.print_statistics()

    def build_index(self) -> None:
        """Build the inverted index from crawled documents."""
        print("\n" + "=" * 70)
        print("STEP 2: BUILDING INVERTED INDEX")
        print("=" * 70)

        if self.spider is None:
            raise RuntimeError("Spider must be run before building index")

        # Get crawled documents and anchor texts
        documents = self.spider.get_crawled_documents()
        anchor_texts = self.spider.get_all_anchor_texts()

        # Create indexer and build index (no zip needed - spider already extracted content)
        self.indexer = HtmlIndexer()
        self.indexer.build_index_from_crawled_documents(documents, anchor_texts)

        # Create query processor
        self.query_processor = QueryProcessor(self.indexer)

        print("\n✓ Index built successfully!")

    def search(self, query: str) -> None:
        """
        Search the indexed documents.

        Args:
            query: Search query
        """
        if self.query_processor is None:
            raise RuntimeError("Index must be built before searching")

        results = self.query_processor.process_query(query)

        if results:
            query_type = self.query_processor.get_query_type_description(query)
            print(f"\nQuery type: {query_type}")
            print(f"Found {len(results)} documents:\n")

            for i, result in enumerate(results[:20], 1):
                score_str = f"{result.score:.4f}" if result.score < 1.0 else f"{result.score:.2f}"
                original_url = self.indexer.get_original_path(result.doc_id)
                print(f"  {i}. {result.doc_id} (score: {score_str})")
                if original_url:
                    print(f"      URL: {original_url}")

            if len(results) > 20:
                print(f"\n  ... and {len(results) - 20} more documents")
        else:
            print("No matches found")

    def interactive_search(self) -> None:
        """Run interactive search loop."""
        if self.query_processor is None:
            raise RuntimeError("Index must be built before searching")

        print("\n" + "=" * 70)
        print("STEP 3: INTERACTIVE SEARCH")
        print("=" * 70)

        # Display statistics
        file_count = self.indexer.get_file_count()
        vocab_size = self.indexer.get_vocabulary_size()
        url_count = len(self.indexer.get_all_urls())
        avg_doc_length = self.indexer.avg_doc_length

        print(f"Indexed {file_count} files with {vocab_size} unique words")
        print(f"Extracted {url_count} URLs from documents")
        print(f"Average document length: {avg_doc_length:.2f} words")

        print("\nQuery Types Supported:")
        print('- Boolean OR: "cat or dog or rat"')
        print('- Boolean AND: "cat and dog and rat"')
        print('- Boolean NOT: "cat but dog"')
        print('- Phrase: "\\"information retrieval evaluation\\""')
        print('- Vector Space: "cat dog rat"')
        print('- Legacy search: "!searchterm" (old format)\n')
        print("Now the search begins:")

        while True:
            try:
                search_term = input("enter a search query=> ")

                # Empty string exits the loop
                if not search_term.strip():
                    break

                self.search(search_term)

            except KeyboardInterrupt:
                print("\n")
                break
            except EOFError:
                break

        print("Bye")

    def run_full_pipeline(self, max_pages: int = None, interactive: bool = True) -> None:
        """
        Run the complete pipeline: spider -> index -> search.

        Args:
            max_pages: Maximum pages to crawl (None for all)
            interactive: Whether to run interactive search after indexing
        """
        try:
            # Step 1: Spider
            self.run_spider(max_pages=max_pages)

            # Step 2: Build index
            self.build_index()

            # Step 3: Interactive search
            if interactive:
                self.interactive_search()
            else:
                print("\n✓ Pipeline completed successfully!")
                print("Use interactive_search() to start searching.")

        except FileNotFoundError:
            print(f"\n✗ Error: {self.zip_path} not found!")
            print("Please make sure the zip file exists in the current directory.")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error during pipeline execution: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point."""
    print("Information Retrieval and Web Search Engine - Part 3")
    print("Spidering and Indexing the Entire Corpus")
    print("=" * 70)

    # Parse command line arguments
    zip_file = "rfh.zip" if len(sys.argv) < 2 else sys.argv[1]
    start_file = "rhf/index.html" if len(sys.argv) < 3 else sys.argv[2]

    # Create and run application
    app = Part3Application(zip_file, start_file)

    # Run full pipeline
    app.run_full_pipeline(interactive=True)


if __name__ == "__main__":
    main()
