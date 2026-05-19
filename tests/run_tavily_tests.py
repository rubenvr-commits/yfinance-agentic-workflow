#!/usr/bin/env python3
"""
Validation script: Run tavily-research API migration tests

Executes all tests in test_tavily_api_migration.py to validate:
- TavilyAPIClient initialization
- search_criterion() returns normalized results
- API error handling
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Execute tavily API migration tests."""
    test_file = Path(__file__).parent / "test_tavily_api_migration.py"
    
    print(f"\nRunning Tavily Research API Migration Tests")
    print(f"{'='*70}")
    print(f"Test file: {test_file}")
    print(f"{'='*70}\n")
    
    # Run test file directly with Python
    result = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=False,
        text=True
    )
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
