#!/usr/bin/env python3
"""
Tavily Research Skill - Investigates a financial asset using Tavily API

This script researches a company across 4 dimensions:
1. Long-term vision and strategic direction
2. Corporate values and philosophy
3. Competitive advantages
4. Critical management decisions during difficult moments

Output: evaluaciones/{ticker}/raw-search/web-search.json
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
import logging

# Add scripts directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import TavilyAPIClient


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TavilyResearcherAPI:
    """
    Conducts structured research on financial assets using Tavily API.
    """
    
    def __init__(self, ticker: str, company_name: str = None, sector: str = None, output_dir: str = None):
        """
        Initialize researcher.
        
        Args:
            ticker: Stock ticker symbol (e.g., "REP.MC")
            company_name: Full company name (optional)
            sector: Industry sector (optional)
            output_dir: Base output directory (defaults to project root/evaluaciones)
        """
        self.ticker = ticker
        self.company_name = company_name or ticker
        self.sector = sector or "Unknown"
        
        # Setup output directory
        if output_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent.parent.parent  # Back to project root
            output_dir = project_root / "evaluaciones" / ticker / "raw-search"
        else:
            output_dir = Path(output_dir) / ticker / "raw-search"
        
        self.output_dir = Path(output_dir)
        self.output_file = self.output_dir / "web-search.json"
        
        # Initialize API client
        self.client = TavilyAPIClient()
        
        # Results container
        self.all_results = {}
        self.failed_criteria = []
    
    
    def run(self) -> bool:
        """
        Execute full research workflow.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n{'='*70}")
            print(f"Tavily Research (API) - {self.company_name} ({self.ticker})")
            print(f"{'='*70}\n")
            
            # Define search queries for each criterion
            print(f"[1] Setting up search queries...\n")
            
            searches = {
                "vision": {
                    "broad": f"{self.company_name} long-term vision strategic direction future plans energy transition 2030 2035",
                    "focused": [
                        f"{self.company_name} vision 2030 strategy"
                    ]
                },
                "values": {
                    "broad": f"{self.company_name} corporate values mission ESG sustainability",
                    "focused": [
                        f"{self.company_name} corporate values mission"
                    ]
                },
                "competitive_advantages": {
                    "broad": f"{self.company_name} competitive advantages differentiation market position",
                    "focused": [
                        f"{self.company_name} competitive advantages strengths"
                    ]
                },
                "critical_decisions": {
                    "broad": f"{self.company_name} management decisions crisis strategic pivots",
                    "focused": [
                        f"{self.company_name} major business decisions"
                    ]
                }
            }
            
            print(f"[2] Executing searches for {self.company_name}...\n")
            
            # Execute searches for each criterion
            for criterion, queries in searches.items():
                self._search_criterion(criterion, queries["broad"], queries["focused"])
            
            print(f"\n[3] Organizing results into JSON...\n")
            
            # Build final output
            output_data = self._build_output(searches)
            
            print(f"[4] Saving results to {self.output_file}...\n")
            
            # Create output directory and save
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[OK] Results saved to: {self.output_file}")
            
            # Summary
            self._print_summary()
            
            return True
        
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return False
        
        finally:
            self.client.close()
    
    
    def _search_criterion(self, criterion: str, broad_query: str, focused_queries: list):
        """
        Execute search for a single criterion with fallback strategy.
        
        Args:
            criterion: Criterion name (vision, values, etc.)
            broad_query: Initial broad search query
            focused_queries: List of fallback focused queries
        """
        result = {
            "criterion": criterion,
            "query_used": None,
            "results": [],
            "status": "pending"
        }
        
        try:
            print(f"  [*] Searching for {criterion}...")
            print(f"      Query: {broad_query[:70]}...")
            
            # Attempt broad query with advanced search depth
            search_result = self.client.search_criterion(broad_query, max_results=3, search_depth="advanced")
            
            if search_result.get("results") and len(search_result["results"]) >= 1:
                result["results"] = search_result["results"]
                result["query_used"] = broad_query
                # attach request metrics if provided by client
                if isinstance(search_result, dict) and search_result.get("request_metrics"):
                    result["request_metrics"] = search_result.get("request_metrics")
                result["status"] = "completed"
                print(f"      [OK] Found {len(result['results'])} results")
            else:
                # Try focused queries if broad search is thin
                print(f"      [WARN] Broad query returned few results, trying focused queries...")
                
                for focused_query in focused_queries:
                    print(f"      Query: {focused_query[:70]}...")
                    focused_result = self.client.search_criterion(focused_query, max_results=3, search_depth="basic")
                    
                    if focused_result.get("results"):
                        result["results"].extend(focused_result["results"])
                        result["query_used"] = focused_query
                        if focused_result.get("request_metrics"):
                            # merge or attach metrics for focused query
                            result.setdefault("request_metrics", {})[focused_query] = focused_result.get("request_metrics")
                        result["status"] = "completed"
                        print(f"      [OK] Found {len(focused_result['results'])} results")
                        
                        if len(result["results"]) >= 1:
                            break
                
                if not result["results"]:
                    result["status"] = "no_results"
                    print(f"      [FAIL] No results found")
                    self.failed_criteria.append(criterion)
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"      [FAIL] Error: {e}")
            self.failed_criteria.append(criterion)
        
        self.all_results[criterion] = result
    
    
    def _build_output(self, searches: dict) -> dict:
        """
        Build final output JSON with consistent schema.
        
        Args:
            searches: Dictionary of searches (not used but kept for compatibility)
        
        Returns:
            Complete output JSON object
        """
        output = {
            "metadata": {
                "ticker": self.ticker,
                "company_name": self.company_name,
                "sector": self.sector,
                "search_date": datetime.now().isoformat(),
                "search_status": "partial_failure" if self.failed_criteria else "completed",
                "failed_criteria": self.failed_criteria
            },
            "vision": {
                "query_used": self.all_results.get("vision", {}).get("query_used"),
                "results": self.all_results.get("vision", {}).get("results", []),
                "request_metrics": self.all_results.get("vision", {}).get("request_metrics")
            },
            "values": {
                "query_used": self.all_results.get("values", {}).get("query_used"),
                "results": self.all_results.get("values", {}).get("results", []),
                "request_metrics": self.all_results.get("values", {}).get("request_metrics")
            },
            "competitive_advantages": {
                "query_used": self.all_results.get("competitive_advantages", {}).get("query_used"),
                "results": self.all_results.get("competitive_advantages", {}).get("results", []),
                "request_metrics": self.all_results.get("competitive_advantages", {}).get("request_metrics")
            },
            "critical_decisions": {
                "query_used": self.all_results.get("critical_decisions", {}).get("query_used"),
                "results": self.all_results.get("critical_decisions", {}).get("results", []),
                "request_metrics": self.all_results.get("critical_decisions", {}).get("request_metrics")
            }
        }
        
        return output
    
    
    def _print_summary(self):
        """Print execution summary."""
        total_results = sum(len(r.get("results", [])) for r in self.all_results.values())
        successful = 4 - len(self.failed_criteria)
        
        print(f"\n{'='*70}")
        print(f"RESEARCH SUMMARY")
        print(f"{'='*70}")
        print(f"  Asset: {self.company_name} ({self.ticker})")
        print(f"  Sector: {self.sector}")
        print(f"  Total criteria searched: 4")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(self.failed_criteria)}")
        if self.failed_criteria:
            print(f"  Failed criteria: {', '.join(self.failed_criteria)}")
        print(f"  Total results collected: {total_results}")
        print(f"  Output file: {self.output_file}")
        print(f"{'='*70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Research a financial asset using Tavily API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python researcher.py --ticker REP.MC
  python researcher.py --ticker REP.MC --company-name "Repsol, S.A." --sector "Energy / Oil & Gas"
  python researcher.py --ticker AAPL --company-name "Apple Inc." --sector "Technology"
        """
    )
    
    parser.add_argument(
        "--ticker",
        required=True,
        help="Stock ticker symbol (e.g., REP.MC, AAPL)"
    )
    parser.add_argument(
        "--company-name",
        help="Full company name (optional, defaults to ticker)"
    )
    parser.add_argument(
        "--sector",
        help="Industry sector (optional)"
    )
    parser.add_argument(
        "--output-dir",
        help="Base output directory (optional, defaults to project root/evaluaciones)"
    )
    
    args = parser.parse_args()
    
    # Create and run researcher
    researcher = TavilyResearcherAPI(
        ticker=args.ticker,
        company_name=args.company_name,
        sector=args.sector,
        output_dir=args.output_dir
    )
    
    success = researcher.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
