#!/usr/bin/env python3
"""
Data Structure Visualization for HTML Search Engine - Part 2

This script visualizes the internal data structures of the enhanced indexer
including inverted index, document records, and URL tracking.
"""

import json
import math
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor
from pprint import pprint

def print_section(title, char="="):
    """Print a formatted section header."""
    print(f"\n{char * 60}")
    print(f" {title}")
    print(f"{char * 60}")

def visualize_document_list(indexer, limit=5):
    """Visualize the document list structure."""
    print_section("DOCUMENT LIST STRUCTURE")
    print("Format: doc_id -> DocumentRecord(doc_id, url, length, unique_words)")
    print()

    count = 0
    for doc_id, record in indexer.document_list.items():
        if count >= limit:
            print(f"... and {len(indexer.document_list) - limit} more documents")
            break

        print(f"Document ID: {doc_id}")
        print(f"  URL: {record.url}")
        print(f"  Total words: {record.length}")
        print(f"  Unique words: {record.unique_words}")
        print(f"  Avg word frequency: {record.length / record.unique_words:.2f}")
        print()
        count += 1

def visualize_inverted_index(indexer, words=None, limit=3):
    """Visualize the inverted index structure."""
    print_section("INVERTED INDEX STRUCTURE")
    print("Format: word -> InvertedIndexEntry(word, doc_frequency, postings[])")
    print("PostingRecord: (doc_id, term_frequency, tf_idf, positions[])")
    print()

    if words is None:
        # Show some interesting words
        words = ['web', 'page', 'home', 'email', 'information']

    for word in words:
        entry = indexer.get_inverted_index_entry(word)
        if entry:
            print(f"Word: '{word}'")
            print(f"  Document Frequency: {entry.document_frequency} documents")
            print(f"  Postings ({len(entry.postings)} total):")

            for i, posting in enumerate(entry.postings[:limit]):
                doc_name = posting.doc_id.replace('./Jan/', '').replace('./', '')
                print(f"    {i+1}. {doc_name}")
                print(f"       Term Frequency: {posting.term_frequency}")
                print(f"       TF-IDF Score: {posting.tf_idf:.6f}")
                print(f"       Positions: {posting.positions[:10]}" +
                      ("..." if len(posting.positions) > 10 else ""))

            if len(entry.postings) > limit:
                print(f"    ... and {len(entry.postings) - limit} more documents")
            print()
        else:
            print(f"Word: '{word}' - NOT FOUND")
            print()

def visualize_url_tracking(indexer, limit=10):
    """Visualize URL extraction and tracking."""
    print_section("URL TRACKING STRUCTURE")
    print("Extracted URLs with status tracking (for future crawler)")
    print()

    urls = indexer.get_all_urls()[:limit]
    for i, url in enumerate(urls, 1):
        status = indexer.get_url_status(url)
        print(f"{i:2d}. {url} (status: {status})")

    if len(indexer.get_all_urls()) > limit:
        print(f"... and {len(indexer.get_all_urls()) - limit} more URLs")
    print(f"\nTotal URLs extracted: {len(indexer.get_all_urls())}")

def visualize_stop_words(indexer):
    """Show stop words configuration."""
    print_section("STOP WORDS CONFIGURATION")
    print("Stop words are filtered out during tokenization")
    print()
    stop_words = sorted(list(indexer.stop_words))
    print("Stop words list:")
    for i in range(0, len(stop_words), 10):
        chunk = stop_words[i:i+10]
        print("  " + ", ".join(f"'{word}'" for word in chunk))

def visualize_tf_idf_calculation(indexer, word="web"):
    """Show TF-IDF calculation details."""
    print_section("TF-IDF CALCULATION EXAMPLE")
    print(f"Example calculation for word: '{word}'")
    print()

    entry = indexer.get_inverted_index_entry(word)
    if not entry:
        print(f"Word '{word}' not found in index")
        return

    print(f"Word: '{word}'")
    print(f"Document Frequency (DF): {entry.document_frequency}")
    print(f"Total Documents (N): {indexer.total_documents}")
    print(f"IDF = log(N/DF) = log({indexer.total_documents}/{entry.document_frequency}) = {entry.document_frequency and math.log(indexer.total_documents/entry.document_frequency):.6f}")
    print()

    print("TF-IDF for each document:")
    for posting in entry.postings[:3]:
        doc_name = posting.doc_id.replace('./Jan/', '').replace('./', '')
        doc_record = indexer.get_document_record(posting.doc_id)
        tf = posting.term_frequency / doc_record.length
        print(f"  {doc_name}:")
        print(f"    Term Frequency (TF): {posting.term_frequency}/{doc_record.length} = {tf:.6f}")
        print(f"    TF-IDF: {posting.tf_idf:.6f}")

def visualize_query_processing():
    """Show query processing examples."""
    print_section("QUERY PROCESSING EXAMPLES")

    indexer = HtmlIndexer('Jan.zip')
    indexer.build_index()
    processor = QueryProcessor(indexer)

    queries = [
        'web',
        'web or page',
        'web and page',
        'web but page',
        '"web page"'
    ]

    for query in queries:
        print(f"Query: {query}")
        query_type, terms, metadata = processor.parse_query(query)
        print(f"  Type: {query_type}")
        print(f"  Terms: {terms}")
        if metadata:
            print(f"  Metadata: {metadata}")

        results = processor.process_query(query)
        print(f"  Results: {len(results)} documents")
        if results:
            top = results[0]
            doc_name = top.doc_id.replace('./Jan/', '').replace('./', '')
            print(f"  Top result: {doc_name} (score: {top.score:.6f})")
        print()

def main():
    """Main visualization function."""
    print("HTML Search Engine - Data Structure Visualization")
    print("=" * 60)

    # Initialize indexer
    print("Initializing indexer...")
    indexer = HtmlIndexer('Jan.zip')
    indexer.build_index()
    print(f"✓ Loaded {indexer.get_file_count()} documents")
    print(f"✓ Built vocabulary of {indexer.get_vocabulary_size()} words")

    # Visualize each data structure
    visualize_document_list(indexer)
    visualize_inverted_index(indexer)
    visualize_url_tracking(indexer)
    visualize_stop_words(indexer)

    visualize_tf_idf_calculation(indexer)
    visualize_query_processing()

    print_section("SUMMARY")
    print(f"Documents indexed: {len(indexer.document_list)}")
    print(f"Vocabulary size: {len(indexer.inverted_index)}")
    print(f"URLs extracted: {len(indexer.get_all_urls())}")
    print(f"Average document length: {indexer.avg_doc_length:.2f} words")
    print(f"Stop words configured: {len(indexer.stop_words)}")

if __name__ == "__main__":
    main()