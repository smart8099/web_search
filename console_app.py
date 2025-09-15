"""
Console Application for HTML Search Engine

This module provides a command-line interface for searching through indexed HTML files.
"""

from typing import Optional
from html_indexer import HtmlIndexer


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
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the indexer by processing all HTML files.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self.indexer.build_index()
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
            print(f"Indexed {file_count} files with {vocab_size} unique words")
    
    def search_and_display(self, search_term: str) -> None:
        """
        Search for a term and display the results.
        
        Args:
            search_term: The term to search for
        """
        if not self.is_initialized:
            print("Error: Indexer not initialized")
            return
            
        if not search_term.strip():
            return
            
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
        print("\nNow the search begins:")
        
        while True:
            try:
                search_term = input("enter a search key=> ")
                
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