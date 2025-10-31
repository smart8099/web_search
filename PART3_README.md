# Project Part 3: Spidering and Indexing the Entire Corpus

Information Retrieval and Web Search Engine Project

## Overview

Part 3 implements a breadth-first web spider that crawls HTML documents starting from an index file, extracts anchor texts, and builds an enhanced inverted index with anchor text support.

## Key Features

### 1. Breadth-First Web Spider (`web_spider.py`)
- **Strategy**: Breadth-first search (BFS) for systematic crawling
- **Starting point**: `rhf/index.html` in `rfh.zip`
- **Features**:
  - Discovers all linked HTML/HTM files in the corpus
  - Extracts anchor texts from all links
  - Tracks crawling statistics (pages crawled, links found, etc.)
  - Handles URL normalization and duplicate detection
  - Builds URL graph showing document connections

### 2. Enhanced Indexer with Anchor Text Support (`html_indexer.py`)
- **New method**: `build_index_from_crawled_documents()`
- **Anchor text handling**:
  - Extracts anchor texts from links pointing to each document
  - Includes anchor texts in index (weighted 2x for importance)
  - Stores anchor texts for display in search results
- **Enhanced features**:
  - Full TF-IDF calculation with anchor text boost
  - Position tracking for phrase queries
  - Document metadata preservation

### 3. Integrated Applications

#### Console Application (`main_part3.py`)
```bash
python3 main_part3.py [zip_file] [start_file]

# Examples:
python3 main_part3.py rfh.zip rhf/index.html
python3 main_part3.py  # Uses defaults
```

**Features**:
- Step-by-step pipeline visualization
- Spider statistics display
- Interactive search interface
- Clickable results with document paths

#### Web Interface (`app_web.py`)
```bash
streamlit run app_web.py
```

**Part 3 Features**:
- ✅ Corpus selection (Jan.zip or rfh.zip)
- ✅ Spider integration toggle
- ✅ **Clickable search results** (Part 3 requirement)
- ✅ Anchor text display in results
- ✅ Spider statistics dashboard
- ✅ Enhanced UI with Part 3 features

## How to Use

### Option 1: Web Interface (Recommended)

1. Place `rfh.zip` in the project directory
2. Run the web interface:
   ```bash
   streamlit run app_web.py
   ```
3. Select "rfh.zip (Part 3 - with Spider)" from the corpus dropdown
4. Check "Use Spider (Part 3)" option
5. Wait for spider to crawl and index documents
6. Search and click on results!

### Option 2: Console Application

1. Place `rfh.zip` in the project directory
2. Run the console app:
   ```bash
   python3 main_part3.py
   ```
3. Wait for the 3-step pipeline:
   - Step 1: Web Spidering
   - Step 2: Building Inverted Index
   - Step 3: Interactive Search
4. Enter search queries and view results

### Option 3: Test Spider Standalone

```bash
python3 web_spider.py [zip_file] [start_file]

# Example:
python3 web_spider.py rfh.zip rhf/index.html
```

## Implementation Details

### Breadth-First Crawling Algorithm

1. **Initialize**: Start with `rhf/index.html`
2. **Queue**: Use deque for BFS traversal
3. **Visit**: Extract HTML content from zip
4. **Discover**: Find all links and anchor texts
5. **Enqueue**: Add unvisited URLs to queue
6. **Repeat**: Until queue is empty or max pages reached

### Anchor Text Processing

Anchor texts are:
- Extracted from `<a>` tags during crawling
- Stored per target URL
- Added to document content during indexing (2x weight)
- Displayed in search results for transparency

### Data Structures

```python
# Spider
html_documents: Dict[str, str]           # url -> html_content
anchor_texts: Dict[str, List[str]]       # url -> [anchor_texts]
url_graph: Dict[str, List[str]]          # url -> [outgoing_links]

# Indexer (enhanced)
anchor_texts: Dict[str, List[str]]       # doc_id -> [anchor_texts]
inverted_index: Dict[str, InvertedIndexEntry]
document_list: Dict[str, DocumentRecord]
```

## Requirements Met

### Task 1: Spidering and Indexing ✅
- [x] Spider implemented with breadth-first strategy
- [x] Starts from `rhf/index.html`
- [x] Collects all HTML/HTM files from corpus
- [x] Indexes only HTML files
- [x] Applies Part 2 indexer to each page
- [x] **Anchor texts extracted and included in indices**

### Task 2: Testing and Interface ✅
- [x] Interfaces work with entire corpus
- [x] **Search results are clickable**
- [x] Enhanced web interface
- [x] Console interface maintained
- [x] Statistics and debugging info

## Project Structure

```
project_work/
├── web_spider.py              # Breadth-first web spider
├── html_indexer.py            # Enhanced indexer (with anchor texts)
├── main_part3.py              # Console app for Part 3
├── app_web.py                 # Web interface (updated for Part 3)
├── query_processor.py         # Query processing (from Part 2)
├── console_app.py             # Console app (from Part 2)
├── PART3_README.md            # This file
├── WEB_INTERFACE.md           # Web interface docs
└── rfh.zip                    # Corpus (to be downloaded)
```

## Testing

### Test Spider Only
```bash
python3 web_spider.py rfh.zip rhf/index.html
```

### Test Full Pipeline
```bash
python3 main_part3.py
```

### Test Web Interface
```bash
streamlit run app_web.py
```

## Statistics Example

After running the spider on rfh.zip, you should see:

```
CRAWLING STATISTICS
==============================================================
Pages successfully crawled: XXX
Total links found: XXXX
Unique URLs discovered: XXX
URLs with anchor texts: XXX
Average links per page: XX.XX
==============================================================
```

## Notes

1. **Breadth-First Strategy**: Ensures systematic exploration of document graph
2. **Anchor Text Weight**: Anchor texts are added 2x to boost relevance
3. **Clickable Results**: Links use document paths for easy access
4. **Backward Compatibility**: Part 2 features still work with Jan.zip
5. **Performance**: Spider caches results for faster subsequent searches

## Troubleshooting

### Spider Not Finding Documents
- Ensure `rfh.zip` is in the project directory
- Check that `rhf/index.html` exists in the zip
- Verify zip file is not corrupted

### Search Results Not Clickable
- Make sure you're using the web interface
- Check that original paths are being stored correctly
- Verify browser allows file:// links

### Performance Issues
- Large corpus may take time to crawl
- Index building is cached - subsequent runs are faster
- Consider limiting max_pages for testing

## Future Enhancements

- [ ] Parallel crawling for better performance
- [ ] Robots.txt support
- [ ] Page ranking (PageRank algorithm)
- [ ] Duplicate detection
- [ ] Content-based clustering
- [ ] Advanced link analysis

## Authors

[Your Name and ID]
[Group Member Names and IDs]

## Course

CSCI 6373 IR and Web Search Engine
Project Part 3: Spidering and Indexing
