"""
HTML Search Engine - Main Entry Point

Information Retrieval and Web Search Engine Project - Part 1
A simple HTML parser and search engine for processing HTML files from Jan.zip

Author: [Your Name and ID]
Course: CSCI 6373 IR and Web Search Engine
"""

from console_app import ConsoleApp


def main() -> None:
    """
    Main entry point for the HTML Search Engine.
    
    This function creates and runs the console application which:
    1. Processes all HTML files from Jan.zip
    2. Extracts index terms (alphabetic words only)  
    3. Provides interactive search functionality
    """
    print("HTML Search Engine - Part 1")
    print("=" * 40)
    
    # Create and run the console application
    app = ConsoleApp("Jan.zip")
    app.run()


if __name__ == "__main__":
    main()