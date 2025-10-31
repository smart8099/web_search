"""
Query Processor for Information Retrieval and Web Search Engine Project - Part 2

This module handles query parsing and processing for different types of queries:
- Boolean queries (OR, AND, NOT)
- Vector space model queries
- Phrasal queries with position matching

Author: [Your Name and ID]
Course: CSCI 6373 IR and Web Search Engine
"""

import re
import math
import heapq
from typing import Dict, List, Set, Optional, Tuple, NamedTuple
from collections import defaultdict, Counter
from html_indexer import HtmlIndexer, PostingRecord


class QueryResult(NamedTuple):
    """Result of a query with relevance score."""
    doc_id: str
    score: float
    snippet: str = ""


class QueryProcessor:
    """
    Processes different types of queries against the inverted index.

    Supports:
    - Boolean queries: OR, AND, NOT operations
    - Vector space model with cosine similarity
    - Phrasal search using word positions
    """

    def __init__(self, indexer: HtmlIndexer):
        """
        Initialize query processor with an indexer.

        Args:
            indexer: HtmlIndexer instance with built index
        """
        self.indexer = indexer

        # Track total results count (before heapq limiting)
        self.last_total_count = 0

        # Query parsing patterns
        self.phrase_pattern = re.compile(r'"([^"]+)"')
        self.boolean_or_pattern = re.compile(r'\b(\w+)\s+or\s+(\w+)', re.IGNORECASE)
        self.boolean_and_pattern = re.compile(r'\b(\w+)\s+and\s+(\w+)', re.IGNORECASE)
        self.boolean_not_pattern = re.compile(r'\b(\w+)\s+but\s+(\w+)', re.IGNORECASE)

    def parse_query(self, query: str) -> Tuple[str, List[str], Dict[str, str]]:
        """
        Parse query to determine type and extract terms.

        Args:
            query: Raw query string

        Returns:
            Tuple of (query_type, terms, metadata)
            query_type: 'phrase', 'boolean_or', 'boolean_and', 'boolean_not', 'vector'
        """
        query = query.strip()

        # Check for phrase query
        phrase_match = self.phrase_pattern.search(query)
        if phrase_match:
            phrase = phrase_match.group(1)
            terms = phrase.lower().split()
            return 'phrase', terms, {'phrase': phrase}

        # Check for boolean queries
        or_match = self.boolean_or_pattern.search(query)
        if or_match:
            terms = [or_match.group(1).lower(), or_match.group(2).lower()]
            # Handle multiple OR terms
            remaining = query.lower()
            for match in self.boolean_or_pattern.finditer(query):
                remaining = remaining.replace(match.group(0), '')
            additional_terms = [t.strip() for t in remaining.split() if t.strip() and t.strip() != 'or']
            all_terms = list(set(terms + additional_terms))
            return 'boolean_or', all_terms, {}

        and_match = self.boolean_and_pattern.search(query)
        if and_match:
            terms = [and_match.group(1).lower(), and_match.group(2).lower()]
            # Handle multiple AND terms
            remaining = query.lower()
            for match in self.boolean_and_pattern.finditer(query):
                remaining = remaining.replace(match.group(0), '')
            additional_terms = [t.strip() for t in remaining.split() if t.strip() and t.strip() != 'and']
            all_terms = list(set(terms + additional_terms))
            return 'boolean_and', all_terms, {}

        not_match = self.boolean_not_pattern.search(query)
        if not_match:
            include_term = not_match.group(1).lower()
            exclude_term = not_match.group(2).lower()
            return 'boolean_not', [include_term, exclude_term], {'include': include_term, 'exclude': exclude_term}

        # Default to vector space model
        terms = [t.lower().strip() for t in query.split() if t.strip()]
        return 'vector', terms, {}

    def boolean_or_search(self, terms: List[str]) -> List[QueryResult]:
        """
        Perform boolean OR search (union of document sets).

        Args:
            terms: List of query terms

        Returns:
            List of QueryResult objects sorted by TF-IDF score
        """
        all_docs = set()
        doc_scores = defaultdict(float)

        for term in terms:
            entry = self.indexer.get_inverted_index_entry(term)
            if entry:
                for posting in entry.postings:
                    all_docs.add(posting.doc_id)
                    doc_scores[posting.doc_id] = max(doc_scores[posting.doc_id], posting.tf_idf)

        results = []
        for doc_id in all_docs:
            results.append(QueryResult(doc_id=doc_id, score=doc_scores[doc_id]))

        # Store total count before limiting
        self.last_total_count = len(results)

        # Use heapq for large result sets (more efficient than full sort)
        if len(results) > 100:
            return heapq.nlargest(100, results, key=lambda x: x.score)
        else:
            return sorted(results, key=lambda x: x.score, reverse=True)

    def boolean_and_search(self, terms: List[str]) -> List[QueryResult]:
        """
        Perform boolean AND search (intersection of document sets).

        Args:
            terms: List of query terms

        Returns:
            List of QueryResult objects sorted by TF-IDF score
        """
        if not terms:
            return []

        # Get documents for each term
        term_docs = []
        term_scores = {}

        for term in terms:
            entry = self.indexer.get_inverted_index_entry(term)
            if entry:
                docs = set(p.doc_id for p in entry.postings)
                term_docs.append(docs)
                for posting in entry.postings:
                    if posting.doc_id not in term_scores:
                        term_scores[posting.doc_id] = {}
                    term_scores[posting.doc_id][term] = posting.tf_idf
            else:
                # If any term is not found, no documents can match
                return []

        # Find intersection
        common_docs = set.intersection(*term_docs) if term_docs else set()

        results = []
        for doc_id in common_docs:
            # Sum TF-IDF scores for all terms
            score = sum(term_scores[doc_id].get(term, 0) for term in terms)
            results.append(QueryResult(doc_id=doc_id, score=score))

        # Store total count before limiting
        self.last_total_count = len(results)

        # Use heapq for large result sets (more efficient than full sort)
        if len(results) > 100:
            return heapq.nlargest(100, results, key=lambda x: x.score)
        else:
            return sorted(results, key=lambda x: x.score, reverse=True)

    def boolean_not_search(self, include_term: str, exclude_term: str) -> List[QueryResult]:
        """
        Perform boolean NOT search (A - B).

        Args:
            include_term: Term that must be present
            exclude_term: Term that must not be present

        Returns:
            List of QueryResult objects sorted by TF-IDF score
        """
        include_entry = self.indexer.get_inverted_index_entry(include_term)
        exclude_entry = self.indexer.get_inverted_index_entry(exclude_term)

        if not include_entry:
            return []

        include_docs = set(p.doc_id for p in include_entry.postings)
        exclude_docs = set(p.doc_id for p in exclude_entry.postings) if exclude_entry else set()

        result_docs = include_docs - exclude_docs

        results = []
        for posting in include_entry.postings:
            if posting.doc_id in result_docs:
                results.append(QueryResult(doc_id=posting.doc_id, score=posting.tf_idf))

        # Store total count before limiting
        self.last_total_count = len(results)

        # Use heapq for large result sets (more efficient than full sort)
        if len(results) > 100:
            return heapq.nlargest(100, results, key=lambda x: x.score)
        else:
            return sorted(results, key=lambda x: x.score, reverse=True)

    def vector_space_search(self, terms: List[str]) -> List[QueryResult]:
        """
        Perform vector space model search using cosine similarity.

        Args:
            terms: List of query terms

        Returns:
            List of QueryResult objects sorted by cosine similarity score
        """
        if not terms:
            return []

        # Calculate query vector (term frequencies)
        query_vector = Counter(terms)
        query_length = math.sqrt(sum(freq * freq for freq in query_vector.values()))

        if query_length == 0:
            return []

        # Get documents containing any query term and build posting lookups
        candidate_docs = set()
        term_postings_by_doc = {}  # {term: {doc_id: posting}}

        for term in set(terms):
            entry = self.indexer.get_inverted_index_entry(term)
            if entry:
                # Create fast lookup dict for this term's postings
                postings_dict = {p.doc_id: p for p in entry.postings}
                term_postings_by_doc[term] = postings_dict
                candidate_docs.update(postings_dict.keys())

        # Calculate cosine similarity for each document
        results = []
        for doc_id in candidate_docs:
            doc_vector = {}
            doc_length_squared = 0

            # Get document vector from all terms in document
            doc_record = self.indexer.get_document_record(doc_id)
            if not doc_record:
                continue

            # Fast lookup: O(1) instead of O(n) for each term
            for term in query_vector:
                if term in term_postings_by_doc:
                    postings_dict = term_postings_by_doc[term]
                    if doc_id in postings_dict:
                        posting = postings_dict[doc_id]
                        doc_vector[term] = posting.tf_idf
                        doc_length_squared += posting.tf_idf * posting.tf_idf

            if doc_length_squared == 0:
                continue

            doc_length = math.sqrt(doc_length_squared)

            # Calculate dot product
            dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)

            # Cosine similarity
            cosine_sim = dot_product / (query_length * doc_length)

            if cosine_sim > 0:
                results.append(QueryResult(doc_id=doc_id, score=cosine_sim))

        # Store total count before limiting
        self.last_total_count = len(results)

        # Use heapq for large result sets (more efficient than full sort)
        if len(results) > 100:
            return heapq.nlargest(100, results, key=lambda x: x.score)
        else:
            return sorted(results, key=lambda x: x.score, reverse=True)

    def phrase_search(self, terms: List[str]) -> List[QueryResult]:
        """
        Perform phrase search using word positions.

        Args:
            terms: List of words in the phrase (in order)

        Returns:
            List of QueryResult objects for documents containing the exact phrase
        """
        if not terms:
            return []

        # Get postings for all terms
        term_postings = {}
        for term in terms:
            entry = self.indexer.get_inverted_index_entry(term)
            if entry:
                term_postings[term] = {p.doc_id: p for p in entry.postings}
            else:
                # If any term is missing, phrase cannot exist
                return []

        # Find documents containing all terms
        common_docs = set.intersection(*[set(postings.keys()) for postings in term_postings.values()])

        results = []
        for doc_id in common_docs:
            # Check if terms appear consecutively
            positions_lists = []
            for term in terms:
                posting = term_postings[term][doc_id]
                positions_lists.append(posting.positions)

            # Find consecutive positions
            phrase_found = False
            for start_pos in positions_lists[0]:
                consecutive = True
                for i, positions in enumerate(positions_lists[1:], 1):
                    if (start_pos + i) not in positions:
                        consecutive = False
                        break

                if consecutive:
                    phrase_found = True
                    break

            if phrase_found:
                # Use average TF-IDF of phrase terms as score
                total_score = sum(term_postings[term][doc_id].tf_idf for term in terms)
                avg_score = total_score / len(terms)
                results.append(QueryResult(doc_id=doc_id, score=avg_score))

        # Store total count before limiting
        self.last_total_count = len(results)

        # Use heapq for large result sets (more efficient than full sort)
        if len(results) > 100:
            return heapq.nlargest(100, results, key=lambda x: x.score)
        else:
            return sorted(results, key=lambda x: x.score, reverse=True)

    def process_query(self, query: str) -> List[QueryResult]:
        """
        Process a query and return ranked results.

        Args:
            query: Query string

        Returns:
            List of QueryResult objects sorted by relevance
        """
        if not self.indexer.is_indexed:
            self.indexer.build_index()

        query_type, terms, metadata = self.parse_query(query)

        if query_type == 'phrase':
            return self.phrase_search(terms)
        elif query_type == 'boolean_or':
            return self.boolean_or_search(terms)
        elif query_type == 'boolean_and':
            return self.boolean_and_search(terms)
        elif query_type == 'boolean_not':
            return self.boolean_not_search(metadata['include'], metadata['exclude'])
        elif query_type == 'vector':
            return self.vector_space_search(terms)
        else:
            return []

    def get_query_type_description(self, query: str) -> str:
        """
        Get a description of the query type for user feedback.

        Args:
            query: Query string

        Returns:
            Description of the query type
        """
        query_type, terms, metadata = self.parse_query(query)

        descriptions = {
            'phrase': f'Phrase search for: "{metadata.get("phrase", "")}"',
            'boolean_or': f'Boolean OR search for: {" OR ".join(terms)}',
            'boolean_and': f'Boolean AND search for: {" AND ".join(terms)}',
            'boolean_not': f'Boolean NOT search: {metadata.get("include", "")} BUT NOT {metadata.get("exclude", "")}',
            'vector': f'Vector space search for: {" ".join(terms)}'
        }

        return descriptions.get(query_type, 'Unknown query type')