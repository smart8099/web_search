#!/usr/bin/env python3
"""
Web-based Search Interface for HTML Search Engine
Using Streamlit for the UI

This provides a modern, browser-based interface for searching through
indexed HTML files from Jan.zip.

Usage:
    streamlit run app_web.py
"""

import streamlit as st
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor
from typing import List, Optional


def initialize_search_engine():
    """
    Initialize the search engine components with caching.
    This runs only once and caches the results for better performance.
    """
    if 'indexer' not in st.session_state:
        with st.spinner('Initializing search engine...'):
            indexer = HtmlIndexer("Jan.zip")
            indexer.build_index()
            query_processor = QueryProcessor(indexer)

            st.session_state.indexer = indexer
            st.session_state.query_processor = query_processor
            st.session_state.initialized = True

    return st.session_state.indexer, st.session_state.query_processor


def display_stats(indexer: HtmlIndexer):
    """Display search engine statistics."""
    file_count = indexer.get_file_count()
    vocab_size = indexer.get_vocabulary_size()
    url_count = len(indexer.get_all_urls())
    avg_doc_length = indexer.avg_doc_length

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Indexed Files", file_count)
    with col2:
        st.metric("Unique Words", vocab_size)
    with col3:
        st.metric("Extracted URLs", url_count)
    with col4:
        st.metric("Avg Doc Length", f"{avg_doc_length:.1f}")


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

    # Initialize search engine
    try:
        indexer, query_processor = initialize_search_engine()

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

            **Tips:**
            - Use quotes for exact phrase matching
            - Boolean operators are case-insensitive
            - Results are ranked by relevance (TF-IDF)
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
                                    st.markdown(f"**{i}. {result.doc_id}**")
                                    # Show original path if available
                                    original_path = indexer.get_original_path(result.doc_id)
                                    if original_path:
                                        st.caption(f"Path: {original_path}")

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
                <p>Built with Streamlit | Powered by Python</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except FileNotFoundError:
        st.error("Error: Jan.zip file not found!")
        st.info("Please make sure Jan.zip is in the same directory as this script.")
    except Exception as e:
        st.error(f"Error initializing search engine: {e}")
        st.info("Please check the error message above and try again.")


if __name__ == "__main__":
    main()
