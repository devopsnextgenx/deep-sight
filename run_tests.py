#!/usr/bin/env python3
"""
Test runner for TextExtractor tests.
Run this script to execute all tests for the TextExtractor class.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Run the tests."""
    print("Running TextExtractor tests...")
    print("=" * 50)
    
    # Import and run the tests
    try:
        import unittest
        from tests.processors.test_text_extractor import TestTextExtractor, TestTextExtractorIntegration
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test cases
        suite.addTests(loader.loadTestsFromTestCase(TestTextExtractor))
        suite.addTests(loader.loadTestsFromTestCase(TestTextExtractorIntegration))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"Error importing test modules: {e}")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())