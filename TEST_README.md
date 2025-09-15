# Test Suite for HTML Search Engine

This document describes the comprehensive test suite for the HTML Search Engine project.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_html_indexer.py        # Unit tests for HtmlIndexer class
├── test_console_app.py         # Unit tests for ConsoleApp class  
├── test_integration.py         # Integration tests with real data
└── test_main.py               # Tests for main module
```

## Running Tests

### Run All Tests
```bash
python3 run_tests.py
```

### Run with Different Verbosity Levels
```bash
python3 run_tests.py -v 0    # Quiet mode
python3 run_tests.py -v 1    # Normal mode  
python3 run_tests.py -v 2    # Verbose mode (default)
```

### Run Specific Test Categories
```bash
python3 run_tests.py --unit-only           # Unit tests only
python3 run_tests.py --integration-only    # Integration tests only
python3 run_tests.py -p "test_html*"      # HTML indexer tests only
```

### Check Prerequisites
```bash
python3 run_tests.py --check-zip    # Check if Jan.zip exists
```

## Test Categories

### 1. Unit Tests - HtmlIndexer (15 tests)
- **Initialization**: Tests proper object initialization
- **Word Extraction**: Tests HTML parsing and word filtering
- **Search Operations**: Tests case-insensitive search functionality
- **Data Structure Management**: Tests file counting and vocabulary size
- **Error Handling**: Tests zip file error scenarios

### 2. Unit Tests - ConsoleApp (17 tests)  
- **Initialization**: Tests app startup and indexer initialization
- **User Interface**: Tests input/output handling and display formatting
- **Search Loop**: Tests interactive search workflow
- **Error Handling**: Tests keyboard interrupts, EOF, and initialization failures

### 3. Integration Tests (8 tests)
- **End-to-End Workflow**: Tests complete indexing and search process
- **Real Data Validation**: Tests with actual Jan.zip content
- **Performance**: Tests with all 31 HTML files and 1800+ vocabulary
- **Data Consistency**: Tests dual data structure synchronization

### 4. Main Module Tests (2 tests)
- **Entry Point**: Tests main function execution flow
- **UI Elements**: Tests application title display

## Test Features

### Comprehensive Coverage
- **42 total tests** with 100% pass rate
- **Unit tests** with mocking for isolated testing
- **Integration tests** with real Jan.zip data
- **Edge cases** including empty inputs, missing files, interrupts

### Realistic Test Data
- Uses actual project requirements (music → fab.html)
- Tests all 31 expected HTML files
- Validates 1800+ word vocabulary
- Checks case-insensitive search behavior

### Error Scenarios
- Missing zip files
- Corrupted data
- User interrupts (Ctrl+C)
- Empty search terms
- Network/IO failures

## Test Results Summary

```
Tests run: 42
Failures: 0  
Errors: 0
Skipped: 0
Success rate: 100.0%
```

## Dependencies

Tests require the same dependencies as the main application:
- `beautifulsoup4`
- `lxml` 
- `unittest` (built-in)
- `unittest.mock` (built-in)

## Key Test Validations

✅ **HTML Parsing**: Extracts only alphabetic words, ignores tags/attributes  
✅ **Search Performance**: O(1) lookup times with reverse indexing  
✅ **Case Sensitivity**: Consistent case-insensitive search behavior  
✅ **Data Integrity**: Dual data structures remain synchronized  
✅ **Error Handling**: Graceful handling of all error conditions  
✅ **User Experience**: Proper console output formatting and flow  
✅ **Integration**: End-to-end workflow with real project data