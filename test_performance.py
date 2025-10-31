#!/usr/bin/env python3
"""
Performance Test Script for Part 3

Tests the time taken for:
1. Spider crawling
2. Index building
3. Total time to ready state
"""

import time
import sys
from web_spider import WebSpider
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor


def test_performance(zip_file="rfh.zip", start_file="rhf/index.html"):
    """
    Test and time the complete pipeline.

    Args:
        zip_file: Corpus zip file
        start_file: Starting file for spider
    """
    print("=" * 70)
    print(f"PERFORMANCE TEST: {zip_file}")
    print("=" * 70)
    print()

    # Total timer
    total_start = time.time()

    # ========================================
    # STEP 1: SPIDER CRAWLING
    # ========================================
    print("STEP 1: WEB SPIDER CRAWLING")
    print("-" * 70)

    spider_start = time.time()
    spider = WebSpider(zip_file, start_file)
    spider.crawl_breadth_first()
    spider_end = time.time()

    spider_time = spider_end - spider_start
    print(f"\n⏱️  Spider crawling time: {spider_time:.2f} seconds")

    # Get statistics
    stats = spider.get_statistics()
    print(f"   - Pages crawled: {stats['pages_crawled']}")
    print(f"   - Links found: {stats['total_links_found']}")
    print(f"   - Unique URLs: {stats['unique_urls_discovered']}")
    print(f"   - URLs with anchors: {stats['urls_with_anchor_texts']}")

    if stats['pages_crawled'] > 0:
        pages_per_sec = stats['pages_crawled'] / spider_time
        print(f"   - Speed: {pages_per_sec:.2f} pages/second")

    print()

    # ========================================
    # STEP 2: INDEX BUILDING
    # ========================================
    print("STEP 2: BUILDING INVERTED INDEX")
    print("-" * 70)

    index_start = time.time()

    # Get crawled documents
    documents = spider.get_crawled_documents()
    anchor_texts = spider.get_all_anchor_texts()

    # Build index (no zip file needed - spider already extracted the content)
    indexer = HtmlIndexer()  # Empty constructor - not reading from zip
    indexer.build_index_from_crawled_documents(documents, anchor_texts)

    index_end = time.time()

    index_time = index_end - index_start
    print(f"\n⏱️  Index building time: {index_time:.2f} seconds")
    print(f"   - Documents indexed: {len(indexer.document_list)}")
    print(f"   - Unique words: {len(indexer.inverted_index)}")
    print(f"   - Total URLs extracted: {len(indexer.url_list)}")
    print(f"   - Avg doc length: {indexer.avg_doc_length:.2f} words")

    if len(indexer.inverted_index) > 0:
        words_per_sec = len(indexer.inverted_index) / index_time
        print(f"   - Speed: {words_per_sec:.2f} words/second")

    print()

    # ========================================
    # STEP 3: QUERY PROCESSOR INITIALIZATION
    # ========================================
    print("STEP 3: QUERY PROCESSOR INITIALIZATION")
    print("-" * 70)

    qp_start = time.time()
    query_processor = QueryProcessor(indexer)
    qp_end = time.time()

    qp_time = qp_end - qp_start
    print(f"\n⏱️  Query processor init time: {qp_time:.2f} seconds")

    print()

    # ========================================
    # TOTAL TIME
    # ========================================
    total_end = time.time()
    total_time = total_end - total_start

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Spider crawling:           {spider_time:>8.2f}s  ({spider_time/total_time*100:>5.1f}%)")
    print(f"Index building:            {index_time:>8.2f}s  ({index_time/total_time*100:>5.1f}%)")
    print(f"Query processor init:      {qp_time:>8.2f}s  ({qp_time/total_time*100:>5.1f}%)")
    print("-" * 70)
    print(f"TOTAL TIME TO READY:       {total_time:>8.2f}s")
    print("=" * 70)
    print()

    # ========================================
    # QUICK SEARCH TEST
    # ========================================
    print("QUICK SEARCH TEST")
    print("-" * 70)

    test_queries = ["computer", "information retrieval", "web search"]

    for query in test_queries:
        search_start = time.time()
        results = query_processor.process_query(query)
        search_end = time.time()

        search_time = (search_end - search_start) * 1000  # Convert to ms

        print(f"Query: '{query}'")
        print(f"  - Results: {len(results) if results else 0} documents")
        print(f"  - Time: {search_time:.2f}ms")

        if results:
            print(f"  - Top result: {results[0].doc_id} (score: {results[0].score:.4f})")
        print()

    print("=" * 70)
    print("✓ Performance test complete!")
    print("=" * 70)

    return {
        'spider_time': spider_time,
        'index_time': index_time,
        'qp_time': qp_time,
        'total_time': total_time,
        'pages_crawled': stats['pages_crawled'],
        'unique_words': len(indexer.inverted_index)
    }


def main():
    """Main entry point."""
    # Test with command line args or defaults
    zip_file = sys.argv[1] if len(sys.argv) > 1 else "rhf.zip"
    start_file = sys.argv[2] if len(sys.argv) > 2 else "rhf/index.html"

    try:
        results = test_performance(zip_file, start_file)

        print(f"\n💡 TIP: System is ready for search in {results['total_time']:.2f} seconds")
        print(f"   ({results['pages_crawled']} pages, {results['unique_words']} unique words)")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please make sure the zip file exists in the current directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
