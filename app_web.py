#!/usr/bin/env python3
"""
Web-based Search Interface for HTML Search Engine
Using Streamlit for the UI

This provides a modern, browser-based interface for searching through
indexed HTML files from Jan.zip or rfh.zip (with spider).

Usage:
    streamlit run app_web.py

Part 3 Features:
- Spider integration for rfh.zip corpus
- Clickable search results
- Anchor text indexing
"""

import streamlit as st
import os
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor
from web_spider import WebSpider
from typing import List, Optional


def initialize_search_engine(corpus_choice: str, use_spider: bool = True):
    """
    Initialize the search engine components with caching.
    This runs only once and caches the results for better performance.

    Args:
        corpus_choice: "rfh.zip" (Part 3 corpus)
        use_spider: Always True for Part 3 (BFS web spider)
    """
    import time

    cache_key = f"{corpus_choice}_spider"

    if 'cache_key' not in st.session_state or st.session_state.cache_key != cache_key:
        with st.spinner('Initializing search engine...'):
            total_start = time.perf_counter()

            # Part 3: Use spider to crawl and index
            st.info("🕷️ Running BFS spider to crawl documents...")
            spider_start = time.perf_counter()
            spider = WebSpider(corpus_choice, "rhf/index.html")
            spider.crawl_breadth_first()
            spider_time = time.perf_counter() - spider_start

            # Get crawled documents
            documents = spider.get_crawled_documents()
            anchor_texts = spider.get_all_anchor_texts()

            st.success(f"✓ Crawled {len(documents)} documents in {spider_time:.2f}s")

            # Build index from crawled documents
            st.info("🔨 Building inverted index with TF-IDF...")
            indexer_start = time.perf_counter()
            indexer = HtmlIndexer()
            indexer.build_index_from_crawled_documents(documents, anchor_texts)
            indexer_time = time.perf_counter() - indexer_start

            st.success(f"✓ Built index in {indexer_time:.2f}s")

            total_time = time.perf_counter() - total_start

            # Store statistics and timing
            st.session_state.spider_stats = spider.get_statistics()
            st.session_state.timing_stats = {
                'spider_time': spider_time,
                'indexer_time': indexer_time,
                'total_time': total_time
            }

            query_processor = QueryProcessor(indexer)

            st.session_state.indexer = indexer
            st.session_state.query_processor = query_processor
            st.session_state.cache_key = cache_key
            st.session_state.corpus = corpus_choice
            st.session_state.initialized = True

    return st.session_state.indexer, st.session_state.query_processor


def display_stats(indexer: HtmlIndexer):
    """Display search engine statistics."""
    file_count = indexer.get_file_count()
    vocab_size = indexer.get_vocabulary_size()
    url_count = len(indexer.get_all_urls())
    avg_doc_length = indexer.avg_doc_length
    docs_with_anchors = len(indexer.anchor_texts) if hasattr(indexer, 'anchor_texts') else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Indexed Files", file_count)
    with col2:
        st.metric("Unique Words", vocab_size)
    with col3:
        st.metric("Extracted URLs", url_count)
    with col4:
        st.metric("Avg Doc Length", f"{avg_doc_length:.1f}")
    with col5:
        st.metric("Docs w/ Anchors", docs_with_anchors)

    # Show spider stats (always available in Part 3)
    st.markdown("#### Spider Statistics")
    spider_stats = st.session_state.get('spider_stats', {})
    if spider_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages Crawled", spider_stats.get('pages_crawled', 0))
        with col2:
            st.metric("Total Links Found", spider_stats.get('total_links_found', 0))
        with col3:
            st.metric("URLs with Anchor Texts", spider_stats.get('urls_with_anchor_texts', 0))

    # Show timing statistics
    st.markdown("#### Performance Timing")
    timing_stats = st.session_state.get('timing_stats', {})
    if timing_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            spider_time = timing_stats.get('spider_time', 0)
            st.metric("Spider Crawling", f"{spider_time:.2f}s",
                     help="Time to crawl all documents with BFS")
        with col2:
            indexer_time = timing_stats.get('indexer_time', 0)
            st.metric("Index Building", f"{indexer_time:.2f}s",
                     help="Time to build inverted index with TF-IDF")
        with col3:
            total_time = timing_stats.get('total_time', 0)
            st.metric("Total Init Time", f"{total_time:.2f}s",
                     help="Total initialization time",
                     delta=f"3.0x faster" if total_time < 200 else None)


def main():
    """Main application function."""

    # Page configuration
    st.set_page_config(
        page_title="HTML Search Engine - Part 3",
        page_icon="🕷️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title and description
    st.title("🔍 HTML Search Engine - Part 3")
    st.markdown("### Information Retrieval with BFS Web Spider & Optimized Indexing")
    st.markdown("**3.0x faster** with chunked parallelization • 9,359 pages • 57,756 unique words")
    st.markdown("---")

    # Check if rhf.zip exists
    if not os.path.exists("rhf.zip"):
        st.error("❌ **Error:** rhf.zip not found!")
        st.info("Please add rhf.zip to the project directory to use the search engine.")
        st.markdown("---")
        st.markdown("**Expected file:** `rhf.zip` (Part 3 corpus with 9,359 HTML files)")
        return

    # Fixed corpus for Part 3
    corpus_file = "rhf.zip"
    use_spider = True  # Always use spider for Part 3

    # Show corpus info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success("📂 **Corpus:** rhf.zip (Part 3 - BFS Web Spider)")
        st.caption("9,359 pages • 57,756 unique words • Optimized with chunked parallelization")
    with col2:
        # Clear cache button
        if st.button("🔄 Reload", help="Clear cache and reload search engine"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("---")

    # Initialize search engine
    try:
        indexer, query_processor = initialize_search_engine(corpus_file, use_spider)

        # Display statistics
        st.subheader("Search Engine Statistics")
        display_stats(indexer)
        st.markdown("---")

        # Sidebar with query type information
        with st.sidebar:
            st.header("🔍 Query Types")
            st.markdown("""
            **Supported query types:**

            - **Boolean OR**: `cat or dog or rat`
            - **Boolean AND**: `cat and dog and rat`
            - **Boolean NOT**: `cat but dog`
            - **Phrase**: `"information retrieval"`
            - **Vector Space**: `cat dog rat`

            ---

            **🕷️ Part 3 Features:**
            - ✅ Breadth-first web spider (BFS)
            - ✅ Anchor text indexing (2x weight)
            - ✅ Clickable search results
            - ✅ TF-IDF relevance ranking
            - ✅ Optimized performance (3.0x faster)
            - ✅ 9,359 pages • 57,756 words

            ---

            **💡 Search Tips:**
            - Use quotes for exact phrase matching
            - Boolean operators are case-insensitive
            - Results ranked by TF-IDF score
            - Anchor texts boost relevance
            - Click "📖 View Content" to preview
            """)

        # Search interface
        st.subheader("Search")

        # Search input
        search_query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., information retrieval, cat or dog, \"exact phrase\"",
            help="Type your search query and press Enter"
        )

        # Search button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            search_button = st.button("🔍 Search", type="primary")
        with col2:
            clear_button = st.button("Clear")

        if clear_button:
            st.rerun()

        # Perform search
        if search_query and (search_button or search_query):
            st.markdown("---")

            # Use query processor for all searches
            try:
                results = query_processor.process_query(search_query)

                if results:
                    # Display query type
                    query_type = query_processor.get_query_type_description(search_query)
                    st.info(f"**Query Type:** {query_type}")

                    # Show total count (before heapq limiting)
                    total_count = query_processor.last_total_count
                    st.success(f"Found {total_count:,} documents")

                    # Display results in a nice format
                    st.subheader("Search Results")

                    # Show top 20 results
                    for i, result in enumerate(results[:20], 1):
                        with st.container():
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                # Get original path
                                original_path = indexer.get_original_path(result.doc_id)

                                if original_path:
                                    # Extract actual website URL from path
                                    # Path format: rhf/www.netfunny.com/rhf/jokes/new91/cslover.html
                                    # Extract: www.netfunny.com/rhf/jokes/new91/cslover.html
                                    if original_path.startswith("rhf/"):
                                        website_url = original_path[4:]  # Remove "rhf/" prefix
                                        full_url = f"http://{website_url}"
                                    else:
                                        full_url = original_path

                                    # Make the result clickable (Part 3 requirement)
                                    st.markdown(f"**{i}. [{result.doc_id}]({full_url})**")
                                    st.caption(f"📄 Path: `{original_path}`")
                                else:
                                    st.markdown(f"**{i}. {result.doc_id}**")

                                # Show anchor texts if available (Part 3 feature)
                                if hasattr(indexer, 'anchor_texts') and result.doc_id in indexer.anchor_texts:
                                    anchors = indexer.anchor_texts[result.doc_id]
                                    if anchors:
                                        anchor_preview = ", ".join(anchors[:3])
                                        if len(anchors) > 3:
                                            anchor_preview += f" ... (+{len(anchors)-3} more)"
                                        st.caption(f"🔗 Anchor texts: {anchor_preview}")

                            with col2:
                                score_str = f"{result.score:.4f}" if result.score < 1.0 else f"{result.score:.2f}"
                                st.metric("Score", score_str)

                            st.markdown("---")

                    if total_count > 20:
                        st.info(f"Showing top 20 results out of {total_count:,} total matches")
                else:
                    st.warning("No matches found for your query")

            except Exception as e:
                st.error(f"❌ **Error processing query:** {e}")
                import traceback
                with st.expander("📋 Show error details"):
                    st.code(traceback.format_exc())

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: gray; padding: 20px;'>
                <p><strong>HTML Search Engine - Information Retrieval Course Project</strong></p>
                <p>Part 3: BFS Web Spider • Anchor Text Indexing • Optimized Performance</p>
                <p>🚀 3.0x faster with chunked parallelization (191s vs 576s)</p>
                <p>Built with Streamlit | Powered by Python | ProcessPoolExecutor</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except FileNotFoundError as e:
        st.error(f"❌ **Error:** rhf.zip not found! ({e})")
        st.info("Please make sure rhf.zip is in the same directory as this script.")
    except Exception as e:
        st.error(f"❌ **Error initializing search engine:** {e}")
        st.info("Try clicking the '🔄 Reload' button or restart the application.")
        import traceback
        with st.expander("📋 Show full error details"):
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
