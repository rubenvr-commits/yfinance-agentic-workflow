#!/usr/bin/env python3
"""
Test suite for tavily-research researcher module (TavilyResearcherAPI)

Validates the researcher workflow and integration with TavilyAPIClient.
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / ".github" / "skills" / "tavily-research" / "scripts"
sys.path.insert(0, str(scripts_dir))


def test_tavily_researcher_api_initialization():
    """Test 1: TavilyResearcherAPI initializes with ticker and company name."""
    from researcher import TavilyResearcherAPI
    
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key"}):
        researcher = TavilyResearcherAPI(
            ticker="AAPL",
            company_name="Apple Inc.",
            sector="Technology"
        )
        
        assert researcher.ticker == "AAPL", "Ticker not set correctly"
        assert researcher.company_name == "Apple Inc.", "Company name not set correctly"
        assert researcher.sector == "Technology", "Sector not set correctly"
        assert researcher.client is not None, "Client not initialized"
        assert researcher.output_file.exists() is False, "Output file should not exist before run"
    
    print("PASS: TavilyResearcherAPI initializes correctly")


def test_tavily_researcher_api_output_structure():
    """Test 2: TavilyResearcherAPI builds correct output JSON structure."""
    from researcher import TavilyResearcherAPI
    
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key"}):
        researcher = TavilyResearcherAPI(ticker="TEST", company_name="Test Corp")
        
        # Mock client search results
        mock_result = {
            "results": [
                {
                    "title": "Test Result",
                    "snippet": "Test snippet content",
                    "source": "https://test.com",
                    "relevance_score": 0.9
                }
            ],
            "status": "completed",
            "query_used": "test query"
        }
        
        # Simulate search results for each criterion
        for criterion in ["vision", "values", "competitive_advantages", "critical_decisions"]:
            researcher.all_results[criterion] = mock_result
        
        # Build output
        output = researcher._build_output({})
        
        # Validate metadata structure
        assert "metadata" in output, "Missing metadata section"
        assert output["metadata"]["ticker"] == "TEST", "Ticker not in metadata"
        assert output["metadata"]["company_name"] == "Test Corp", "Company name not in metadata"
        
        # Validate each dimension has correct structure
        for criterion in ["vision", "values", "competitive_advantages", "critical_decisions"]:
            assert criterion in output, f"Missing {criterion} section"
            assert "query_used" in output[criterion], f"Missing query_used in {criterion}"
            assert "results" in output[criterion], f"Missing results in {criterion}"
    
    print("PASS: TavilyResearcherAPI builds correct output structure")


if __name__ == "__main__":
    try:
        test_tavily_researcher_api_initialization()
        test_tavily_researcher_api_output_structure()
        print("\n" + "="*70)
        print("ALL RESEARCHER TESTS PASSED")
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
