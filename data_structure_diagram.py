#!/usr/bin/env python3
"""
ASCII Art Data Structure Diagram for HTML Search Engine - Part 2
"""

def print_data_structure_diagram():
    """Print ASCII art representation of the data structures."""

    print("""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                        HTML SEARCH ENGINE - PART 2 DATA STRUCTURES                ║
╚════════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────┐    ┌─────────────────────────────────────────────────────────────┐
│   HTML FILES    │───▶│                    HTML INDEXER                            │
│   (Jan.zip)     │    │                                                             │
│                 │    │  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│ • aol.html      │    │  │   TOKENIZER     │  │        STOP WORD FILTER          │ │
│ • bill.html     │    │  │                 │  │                                  │ │
│ • kitty.html    │    │  │ • Extract text  │  │ • Remove: 'a', 'the', 'and'     │ │
│ • ...           │    │  │ • Extract URLs  │  │ • Remove: 'is', 'of', 'to'      │ │
│                 │    │  │ • Word positions│  │ • Keep: 'web', 'page', 'email'  │ │
└─────────────────┘    │  └─────────────────┘  └──────────────────────────────────┘ │
                       └─────────────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              CORE DATA STRUCTURES                                   │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  1️⃣  DOCUMENT LIST (Hash Map)                                                       │
│      doc_id ──▶ DocumentRecord(doc_id, url, length, unique_words)                  │
│                                                                                      │
│      "./Jan/kitty.html" ──▶ { doc_id: "./Jan/kitty.html"                          │
│                               url: "Jan/kitty.html"                                │
│                               length: 238                                          │
│                               unique_words: 184 }                                  │
│                                                                                      │
│  ────────────────────────────────────────────────────────────────────────────────   │
│                                                                                      │
│  2️⃣  INVERTED INDEX (Hash Map)                                                      │
│      word ──▶ InvertedIndexEntry(word, doc_frequency, postings[])                  │
│                                                                                      │
│      "web" ──▶ { word: "web"                                                       │
│                  document_frequency: 2                                             │
│                  postings: [                                                       │
│                    PostingRecord(                                                  │
│                      doc_id: "./Jan/bill.html"                                     │
│                      term_frequency: 1                                             │
│                      tf_idf: 0.026871                                              │
│                      positions: [77]                                               │
│                    ),                                                               │
│                    PostingRecord(                                                  │
│                      doc_id: "./Jan/kitty.html"                                    │
│                      term_frequency: 2                                             │
│                      tf_idf: 0.023032                                              │
│                      positions: [40, 81]                                           │
│                    )                                                                │
│                  ] }                                                                │
│                                                                                      │
│  ────────────────────────────────────────────────────────────────────────────────   │
│                                                                                      │
│  3️⃣  URL TRACKING (Lists + Hash Map)                                               │
│      url_list: ["mailto:user@site.com", "image.gif", ...]                         │
│      url_status: { "mailto:user@site.com" ──▶ "unvisited" }                       │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                            QUERY PROCESSOR                                          │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  📝 QUERY TYPES:                                                                    │
│                                                                                      │
│  • Boolean OR:  "cat or dog"     ──▶ Union of document sets                        │
│  • Boolean AND: "cat and dog"    ──▶ Intersection of document sets                 │
│  • Boolean NOT: "cat but dog"    ──▶ Difference of document sets                   │
│  • Phrase:      "\"web page\""     ──▶ Consecutive word positions                    │
│  • Vector:      "cat dog"        ──▶ Cosine similarity with TF-IDF                 │
│                                                                                      │
│  🧮 TF-IDF CALCULATION:                                                             │
│      TF = term_frequency / document_length                                          │
│      IDF = log(total_documents / document_frequency)                                │
│      TF-IDF = TF × IDF                                                              │
│                                                                                      │
│  📊 COSINE SIMILARITY:                                                              │
│      similarity = dot_product(query_vector, doc_vector) /                          │
│                   (||query_vector|| × ||doc_vector||)                              │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                        │
├─────────────────────────────────┬────────────────────────────────────────────────────┤
│           CONSOLE APP           │                    GUI APP                        │
│                                 │                                                    │
│  • Interactive query input      │  • Visual search interface                        │
│  • Query type display           │  • Result cards with scores                       │
│  • Ranked results with scores   │  • Query type identification                      │
│  • Support for all query types  │  • Real-time search                               │
│                                 │  • Statistics display                             │
└─────────────────────────────────┴────────────────────────────────────────────────────┘

""")

def print_example_content():
    """Show example content from actual files."""
    print("📁 SAMPLE FILE CONTENT ANALYSIS")
    print("=" * 80)

    from html_indexer import HtmlIndexer

    indexer = HtmlIndexer('Jan.zip')
    indexer.build_index()

    # Show content of a sample file
    import zipfile
    with zipfile.ZipFile('Jan.zip', 'r') as zip_ref:
        # Get a small file to show
        for file_info in zip_ref.infolist():
            if file_info.filename == 'Jan/bill.html':
                with zip_ref.open(file_info) as html_file:
                    content = html_file.read().decode('utf-8', errors='ignore')

                print(f"\n📄 Raw HTML Content (Jan/bill.html):")
                print("-" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)

                print(f"\n🔍 Extracted Words:")
                print("-" * 50)
                words, positions = indexer.extract_words_with_positions(content)
                print(f"Total words after filtering: {len(words)}")
                print(f"First 20 words: {words[:20]}")

                print(f"\n📍 Word Positions (sample):")
                print("-" * 50)
                for word in ['web', 'page', 'home'][:3]:
                    if word in positions:
                        print(f"'{word}': positions {positions[word]}")

                print(f"\n🔗 Extracted URLs:")
                print("-" * 50)
                urls = indexer.extract_urls_from_html(content)
                for url in urls[:5]:
                    print(f"  • {url}")
                if len(urls) > 5:
                    print(f"  ... and {len(urls) - 5} more URLs")

                break

if __name__ == "__main__":
    print_data_structure_diagram()
    print_example_content()