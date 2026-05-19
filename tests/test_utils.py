#!/usr/bin/env python3
"""
Test suite for tavily-research utils module (TavilyAPIClient)

Re-exports tests from test_tavily_api_migration.py
"""

from test_tavily_api_migration import (
    test_tavily_api_client_initialization,
    test_search_criterion_returns_normalized_results,
    test_search_criterion_handles_api_errors
)

__all__ = [
    "test_tavily_api_client_initialization",
    "test_search_criterion_returns_normalized_results",
    "test_search_criterion_handles_api_errors"
]

if __name__ == "__main__":
    print("Running TavilyAPIClient (utils module) tests...")
    test_tavily_api_client_initialization()
    test_search_criterion_returns_normalized_results()
    test_search_criterion_handles_api_errors()
    print("\nAll utils tests passed.")
