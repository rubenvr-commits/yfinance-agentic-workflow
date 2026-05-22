#!/usr/bin/env python3
"""
Test tavily-research API migration from MCP to HTTP API.

Validates:
1. TavilyAPIClient initialization with API key
2. search_criterion() returns expected schema with normalized results
"""

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / ".github" / "skills" / "tavily-research" / "scripts"
sys.path.insert(0, str(scripts_dir))


def test_tavily_api_client_initialization():
    """Test 1: TavilyAPIClient initializes with API key from environment."""
    # Import inside test to ensure mock is set up first
    from utils import TavilyAPIClient
    
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key-12345"}):
        client = TavilyAPIClient(timeout=30)
        
        # Validate client attributes
        assert client.api_key == "test-api-key-12345", "API key not loaded from environment"
        assert client.timeout == 30, "Timeout not set correctly"
        assert client.API_ENDPOINT == "https://api.tavily.com/search", "API endpoint incorrect"
        
    print("PASS: TavilyAPIClient initializes correctly with API key")


def test_tavily_api_client_initialization_from_root_env():
    """Test 1b: TavilyAPIClient falls back to the repository root .env file."""
    import utils
    from utils import TavilyAPIClient

    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        scripts_dir = project_root / ".github" / "skills" / "tavily-research" / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (project_root / ".env").write_text("TAVILY_API_KEY=root-env-key\n", encoding="utf-8")

        fake_utils_file = scripts_dir / "utils.py"

        with patch.object(utils, "__file__", str(fake_utils_file)):
            with patch.dict(os.environ, {}, clear=True):
                client = TavilyAPIClient(timeout=30)

                assert client.api_key == "root-env-key", "API key not loaded from root .env"
                assert os.environ["TAVILY_API_KEY"] == "root-env-key", "API key not exported to environment"

    print("PASS: TavilyAPIClient falls back to root .env")


def test_search_criterion_returns_normalized_results():
    """Test 2: search_criterion() returns normalized results with correct schema."""
    from utils import TavilyAPIClient
    
    # Mock API response
    mock_response = {
        "success": True,
        "results": [
            {
                "title": "Test Result 1",
                "content": "This is a test result with meaningful content",
                "url": "https://example.com/test1"
            },
            {
                "title": "Test Result 2",
                "content": "Another meaningful result for validation",
                "url": "https://example.com/test2"
            }
        ],
        "answer": "Test AI answer"
    }
    
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
        client = TavilyAPIClient()
        
        # Mock requests.post
        with patch("requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=200, json=lambda: mock_response)
            
            # Execute search
            result = client.search_criterion("test query", max_results=3, search_depth="basic")
            
            # Validate result structure
            assert result["status"] == "completed", f"Expected 'completed', got '{result['status']}'"
            assert "results" in result, "Missing 'results' key"
            assert len(result["results"]) >= 2, f"Expected 2+ results, got {len(result['results'])}"
            
            # Validate first result schema
            first_result = result["results"][0]
            required_keys = {"title", "snippet", "source", "relevance_score"}
            assert set(first_result.keys()) == required_keys, f"Result schema mismatch. Expected {required_keys}, got {set(first_result.keys())}"
            
            # Validate result values
            assert isinstance(first_result["title"], str), "title must be string"
            assert isinstance(first_result["snippet"], str), "snippet must be string"
            assert isinstance(first_result["source"], str), "source must be string"
            assert isinstance(first_result["relevance_score"], float), "relevance_score must be float"
            assert 0.0 <= first_result["relevance_score"] <= 1.0, "relevance_score must be between 0.0 and 1.0"
    
    print("PASS: search_criterion() returns correctly normalized results")


def test_search_criterion_handles_api_errors():
    """Test 3: search_criterion() handles API errors gracefully."""
    from utils import TavilyAPIClient
    
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
        client = TavilyAPIClient()
        
        # Mock failed API response
        with patch("requests.post") as mock_post:
            mock_post.return_value = Mock(status_code=401, text="Unauthorized")
            
            result = client.search_criterion("test query")
            
            assert result["status"] == "error", f"Expected 'error' status, got '{result['status']}'"
            assert result["error"] is not None, "Error message should be populated"
    
    print("PASS: search_criterion() handles API errors")


if __name__ == "__main__":
    # Run tests manually without pytest
    try:
        test_tavily_api_client_initialization()
        test_tavily_api_client_initialization_from_root_env()
        test_search_criterion_returns_normalized_results()
        test_search_criterion_handles_api_errors()
        print("\n" + "="*70)
        print("ALL TESTS PASSED")
        print("="*70)
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        print("="*70)
        sys.exit(1)
    except Exception as e:
        print(f"\nTEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("="*70)
        sys.exit(1)
