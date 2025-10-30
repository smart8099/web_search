# Web-Based Search Interface

This document explains how to use the web-based search interface for the HTML Search Engine.

## Running the Web Interface

To start the web application, run:

```bash
streamlit run app_web.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

## Features

### Search Capabilities
- **Boolean OR**: Search for documents containing any of the terms
  - Example: `cat or dog or rat`

- **Boolean AND**: Search for documents containing all terms
  - Example: `cat and dog and rat`

- **Boolean NOT**: Search for documents with one term but not another
  - Example: `cat but dog`

- **Phrase Search**: Search for exact phrases
  - Example: `"information retrieval"`

- **Vector Space Search**: Ranked search using TF-IDF
  - Example: `cat dog rat`

- **Legacy Search**: Old format search (prefix with `!`)
  - Example: `!searchterm`

### User Interface

1. **Statistics Dashboard**: View indexed files, unique words, and other metrics
2. **Search Bar**: Enter your query and press Enter or click Search
3. **Sidebar**: Quick reference for query types and tips
4. **Results Display**: Shows ranked results with scores and document paths

### Benefits of Web Interface

- Modern, intuitive browser-based UI
- Real-time search results
- No need for command-line interaction
- Better visualization of results
- Easy to share and access from any device on your network

## Stopping the Application

To stop the web server, press `Ctrl+C` in the terminal where you ran the streamlit command.

## Requirements

- Python 3.x
- Streamlit (automatically installed)
- All other dependencies from the project
- Jan.zip file in the same directory

## Troubleshooting

If you encounter issues:

1. Make sure `Jan.zip` is in the project directory
2. Ensure all dependencies are installed: `pip install streamlit beautifulsoup4 lxml`
3. Check that you're running the command from the project directory
4. If the browser doesn't open automatically, manually navigate to `http://localhost:8501`
