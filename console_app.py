"""
Console Application for HTML Search Engine

This module provides a command-line interface for searching through indexed HTML files.
"""

from typing import Optional, List
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor, QueryResult


class ConsoleApp:
    """
    Console application for interactive search through HTML files.
    
    This class provides a command-line interface that allows users to search
    for terms in the indexed HTML files and displays the results.
    """
    
    def __init__(self, zip_path: str = "Jan.zip") -> None:
        """
        Initialize the console application.
        
        Args:
            zip_path: Path to the zip file containing HTML files (default: "Jan.zip")
        """
        self.indexer = HtmlIndexer(zip_path)
        self.query_processor = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the indexer by processing all HTML files.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self.indexer.build_index()
            self.query_processor = QueryProcessor(self.indexer)
            self.is_initialized = True
            return True
        except (FileNotFoundError, Exception) as e:
            print(f"Error initializing indexer: {e}")
            return False
    
    def display_stats(self) -> None:
        """Display statistics about the indexed files."""
        if self.is_initialized:
            file_count = self.indexer.get_file_count()
            vocab_size = self.indexer.get_vocabulary_size()
            url_count = len(self.indexer.get_all_urls())
            print(f"Indexed {file_count} files with {vocab_size} unique words")
            print(f"Extracted {url_count} URLs from documents")
            print(f"Average document length: {self.indexer.avg_doc_length:.2f} words")
    
    def format_results(self, results: List[QueryResult], query: str) -> str:
        """
        Format query results for display.

        Args:
            results: List of QueryResult objects
            query: Original query string

        Returns:
            Formatted string for display
        """
        if not results:
            return "no match"

        # Show query type
        query_type_desc = self.query_processor.get_query_type_description(query)
        output = [f"Query type: {query_type_desc}"]
        output.append(f"Found {len(results)} documents:")

        # Show top results with scores
        for i, result in enumerate(results[:10], 1):  # Show top 10
            # Use the document ID directly (now in format: filename1234)
            doc_name = result.doc_id
            score_str = f"{result.score:.4f}" if result.score < 1.0 else f"{result.score:.2f}"
            output.append(f"  {i}. {doc_name} (score: {score_str})")

        if len(results) > 10:
            output.append(f"  ... and {len(results) - 10} more documents")

        return "\n".join(output)

    def search_and_display(self, search_term: str) -> None:
        """
        Search for a term using the enhanced query processor and display results.

        Args:
            search_term: The query to search for
        """
        if not self.is_initialized:
            print("Error: Indexer not initialized")
            return

        if not search_term.strip():
            return

        # Check if user wants to use legacy search
        if search_term.startswith('!'):
            # Legacy search mode
            legacy_term = search_term[1:].strip()
            results = self.indexer.search_word(legacy_term)
            if results:
                print(f"found a match: {' '.join(results)}")
            else:
                print("no match")
            return

        # Use new query processor
        try:
            results = self.query_processor.process_query(search_term)
            output = self.format_results(results, search_term)
            print(output)
        except Exception as e:
            print(f"Error processing query: {e}")
            # Fallback to legacy search
            results = self.indexer.search_word(search_term)
            if results:
                print(f"found a match: {' '.join(results)}")
            else:
                print("no match")
    
    def run(self) -> None:
        """
        Run the main interactive search loop.
        
        This method provides the main interface where users can enter search terms
        and see results, following the exact format specified in the requirements.
        """
        # Initialize the indexer
        if not self.initialize():
            print("Failed to initialize the search engine. Please check that Jan.zip exists.")
            return
            
        self.display_stats()
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
                    
                self.search_and_display(search_term)
                
            except KeyboardInterrupt:
                print("\n")
                break
            except EOFError:
                break
        
        print("Bye")


def main() -> None:
    """Main entry point for the console application."""
    app = ConsoleApp()
    app.run()


if __name__ == "__main__":
    main()