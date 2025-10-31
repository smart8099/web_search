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


def initialize_search_engine(corpus_choice: str, use_spider: bool = False):
    """
    Initialize the search engine components with caching.
    This runs only once and caches the results for better performance.

    Args:
        corpus_choice: Either "Jan.zip" or "rfh.zip"
        use_spider: Whether to use spider for crawling (Part 3)
    """
    cache_key = f"{corpus_choice}_{'spider' if use_spider else 'direct'}"

    if 'cache_key' not in st.session_state or st.session_state.cache_key != cache_key:
        with st.spinner('Initializing search engine...'):
            if use_spider and corpus_choice == "rfh.zip":
                # Part 3: Use spider to crawl and index
                st.info("🕷️ Running spider to crawl documents...")
                spider = WebSpider(corpus_choice, "rhf/index.html")
                spider.crawl_breadth_first()

                # Get crawled documents
                documents = spider.get_crawled_documents()
                anchor_texts = spider.get_all_anchor_texts()

                st.success(f"✓ Crawled {len(documents)} documents")

                # Build index from crawled documents (no zip needed - spider extracted content)
                st.info("🔨 Building inverted index...")
                indexer = HtmlIndexer()
                indexer.build_index_from_crawled_documents(documents, anchor_texts)

                st.session_state.spider_stats = spider.get_statistics()
            else:
                # Part 2: Direct indexing from zip
                indexer = HtmlIndexer(corpus_choice)
                indexer.build_index()
                st.session_state.spider_stats = None

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

    # Show spider stats if available
    if 'spider_stats' in st.session_state and st.session_state.spider_stats:
        st.markdown("#### Spider Statistics")
        spider_stats = st.session_state.spider_stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages Crawled", spider_stats['pages_crawled'])
        with col2:
            st.metric("Total Links Found", spider_stats['total_links_found'])
        with col3:
            st.metric("URLs with Anchor Texts", spider_stats['urls_with_anchor_texts'])


def main():
    """Main application function."""

    # Page configuration
    st.set_page_config(
        page_title="HTML Search Engine",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title and description
    st.title("🔍 HTML Search Engine")
    st.markdown("### Information Retrieval and Web Search Engine Project")
    st.markdown("---")

    # Corpus selection
    st.subheader("Corpus Selection")
    col1, col2 = st.columns([2, 1])

    with col1:
        # Check which files are available
        available_corpora = []
        if os.path.exists("Jan.zip"):
            available_corpora.append("Jan.zip (Part 2)")
        if os.path.exists("rfh.zip"):
            available_corpora.append("rfh.zip (Part 3 - with Spider)")

        if not available_corpora:
            st.error("No corpus files found! Please add Jan.zip or rfh.zip to the directory.")
            return

        corpus_choice = st.selectbox(
            "Select corpus to search:",
            available_corpora,
            help="Choose which document collection to search"
        )

        # Extract actual filename
        corpus_file = corpus_choice.split()[0]

    with col2:
        use_spider = st.checkbox(
            "Use Spider (Part 3)",
            value=corpus_file == "rfh.zip",
            disabled=corpus_file != "rfh.zip",
            help="Enable breadth-first web spider for crawling documents"
        )

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
            st.header("Query Types")
            st.markdown("""
            **Supported query types:**

            - **Boolean OR**: `cat or dog or rat`
            - **Boolean AND**: `cat and dog and rat`
            - **Boolean NOT**: `cat but dog`
            - **Phrase**: `"information retrieval"`
            - **Vector Space**: `cat dog rat`
            - **Legacy**: `!searchterm`

            ---

            **Part 3 Features:**
            - 🕷️ Breadth-first web spider
            - 🔗 Anchor text indexing
            - 📄 Clickable search results
            - 🎯 Enhanced relevance with anchor texts

            ---

            **Tips:**
            - Use quotes for exact phrase matching
            - Boolean operators are case-insensitive
            - Results are ranked by relevance (TF-IDF)
            - Anchor texts boost document relevance
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

            # Check for legacy search
            if search_query.startswith('!'):
                legacy_term = search_query[1:].strip()
                results = indexer.search_word(legacy_term)

                if results:
                    st.success(f"Found {len(results)} documents (legacy search)")
                    st.write("**Matching documents:**")
                    for i, doc_id in enumerate(results[:20], 1):
                        st.write(f"{i}. {doc_id}")
                else:
                    st.warning("No matches found")
            else:
                # Use query processor
                try:
                    results = query_processor.process_query(search_query)

                    if results:
                        # Display query type
                        query_type = query_processor.get_query_type_description(search_query)
                        st.info(f"**Query Type:** {query_type}")

                        st.success(f"Found {len(results)} documents")

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
                                        # Make the result clickable (Part 3 requirement)
                                        # Create a file:// URL for local files
                                        file_url = f"file://{os.path.abspath(corpus_file)}#{original_path}"
                                        st.markdown(f"**{i}. [{result.doc_id}]({original_path})**")
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

                        if len(results) > 20:
                            st.info(f"Showing top 20 results out of {len(results)} total matches")
                    else:
                        st.warning("No matches found for your query")

                except Exception as e:
                    st.error(f"Error processing query: {e}")
                    # Fallback to legacy search
                    st.info("Trying legacy search...")
                    results = indexer.search_word(search_query)
                    if results:
                        st.success(f"Found {len(results)} documents")
                        for i, doc_id in enumerate(results[:20], 1):
                            st.write(f"{i}. {doc_id}")
                    else:
                        st.warning("No matches found")

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: gray; padding: 20px;'>
                <p>HTML Search Engine - Information Retrieval Course Project</p>
                <p>Part 3: Spider Integration & Clickable Results</p>
                <p>Built with Streamlit | Powered by Python | BFS Web Spider</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except FileNotFoundError as e:
        st.error(f"Error: Corpus file not found! ({e})")
        st.info("Please make sure the selected zip file is in the same directory as this script.")
    except Exception as e:
        st.error(f"Error initializing search engine: {e}")
        st.info("Please check the error message above and try again.")
        import traceback
        with st.expander("Show full error details"):
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
