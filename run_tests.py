#!/usr/bin/env python3
"""
Test runner for HTML Search Engine

This script runs all unit tests and integration tests for the HTML search engine project.
It provides detailed test results and coverage information.
"""

import unittest
import sys
import os
from io import StringIO


def run_tests(verbosity=2, pattern='test*.py'):
    """
    Run all tests in the tests directory.
    
    Args:
        verbosity: Level of test output detail (0=quiet, 1=normal, 2=verbose)
        pattern: Pattern to match test files (default: 'test*.py')
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Ensure the project root is in the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    
    if not os.path.exists(start_dir):
        print(f"Error: Test directory '{start_dir}' not found")
        return False
    
    suite = loader.discover(start_dir, pattern=pattern)
    
    # Run tests with custom result handler
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True,
        failfast=False
    )
    
    print("HTML Search Engine - Test Suite")
    print("=" * 50)
    print(f"Looking for tests in: {start_dir}")
    print(f"Test pattern: {pattern}")
    print("-" * 50)
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Tests run: {total_tests}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    success_rate = 0 if total_tests == 0 else ((total_tests - failures - errors) / total_tests * 100)
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
            
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Return True if all tests passed
    return result.wasSuccessful()


def run_specific_test_class(test_class_name, verbosity=2):
    """
    Run a specific test class.
    
    Args:
        test_class_name: Name of the test class (e.g., 'TestHtmlIndexer')
        verbosity: Level of test output detail
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Ensure the project root is in the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Import test modules
    try:
        if test_class_name.startswith('TestHtml'):
            from tests.test_html_indexer import TestHtmlIndexer
            suite = unittest.TestLoader().loadTestsFromTestCase(TestHtmlIndexer)
        elif test_class_name.startswith('TestConsole'):
            from tests.test_console_app import TestConsoleApp
            suite = unittest.TestLoader().loadTestsFromTestCase(TestConsoleApp)
        elif test_class_name.startswith('TestIntegration'):
            from tests.test_integration import TestIntegration
            suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
        else:
            print(f"Unknown test class: {test_class_name}")
            return False
            
    except ImportError as e:
        print(f"Error importing test class: {e}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main entry point for the test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run tests for HTML Search Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v 1               # Run with minimal output
  python run_tests.py -p "test_html*"    # Run only HTML indexer tests
  python run_tests.py --unit-only        # Run only unit tests
  python run_tests.py --integration-only # Run only integration tests
        """
    )
    
    parser.add_argument(
        '-v', '--verbosity',
        type=int,
        choices=[0, 1, 2],
        default=2,
        help='Test output verbosity (0=quiet, 1=normal, 2=verbose)'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        default='test*.py',
        help='Pattern to match test files (default: test*.py)'
    )
    
    parser.add_argument(
        '--unit-only',
        action='store_true',
        help='Run only unit tests (exclude integration tests)'
    )
    
    parser.add_argument(
        '--integration-only',
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--check-zip',
        action='store_true',
        help='Check if Jan.zip exists before running tests'
    )
    
    args = parser.parse_args()
    
    # Check for Jan.zip if requested
    if args.check_zip:
        if not os.path.exists('Jan.zip'):
            print("Warning: Jan.zip not found. Integration tests will be skipped.")
        else:
            print("Jan.zip found. All tests can run.")
        return
    
    # Determine test pattern based on options
    pattern = args.pattern
    if args.unit_only:
        pattern = 'test_html*.py test_console*.py'  # Exclude integration tests
    elif args.integration_only:
        pattern = 'test_integration*.py'
    
    # Run tests
    success = run_tests(verbosity=args.verbosity, pattern=pattern)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()