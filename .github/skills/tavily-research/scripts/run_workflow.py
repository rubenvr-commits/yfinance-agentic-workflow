#!/usr/bin/env python3
"""
Mini-workflow Orchestrator: Tavily Research → Web Search Fundamentales

This script automates the complete research and fundamentals report generation:
1. Executes tavily-research to generate evaluaciones/{ticker}/raw-search/web-search.json
2. Upon success, automatically invokes web-search-fundamentales to generate evaluaciones/{ticker}/informe-fundamentales.md

Usage:
    python run_workflow.py --ticker REP.MC
    python run_workflow.py --ticker REP.MC --company-name "Repsol, S.A." --sector "Energy / Oil & Gas"
    python run_workflow.py --from-natural "investigar Apple Inc (AAPL)"
"""

import sys
import os
import subprocess
import re
import time
import argparse
from pathlib import Path
from typing import Optional, Tuple


def extract_ticker(input_str: str) -> Optional[str]:
    """
    Extract a valid ticker from user input.
    Supports:
    - Direct input: "AAPL"
    - Explicit: "ticker: AAPL" or "ticker=AAPL"
    - Natural mention: "investigar AAPL", "research MSFT", "evaluate GOOGL"
    """
    input_str = input_str.strip()
    
    # Pattern 1: Direct input (1-5 uppercase chars)
    if re.match(r'^[A-Z]{1,5}$', input_str):
        return input_str.upper()
    
    # Pattern 2: Explicit with "ticker: " or "ticker="
    explicit_match = re.search(r'ticker\s*[:=]\s*([A-Z0-9]{1,5})', input_str, re.IGNORECASE)
    if explicit_match:
        return explicit_match.group(1).upper()
    
    # Pattern 3: Natural mention - word in parentheses
    paren_match = re.search(r'\(([A-Z0-9]{1,5})\)', input_str)
    if paren_match:
        return paren_match.group(1).upper()
    
    # Pattern 4: Natural mention - word after common verbs
    verb_pattern = r'(?:investigar|analizar|research|evaluate|valora|estima|compara)\s+(?:[^()]*?)?\s*([A-Z0-9]{1,5})(?:\s|$|\.)'
    verb_match = re.search(verb_pattern, input_str, re.IGNORECASE)
    if verb_match:
        ticker = verb_match.group(1).upper()
        if 1 <= len(ticker) <= 5:
            return ticker
    
    # Pattern 5: Any 1-5 uppercase chars (fallback)
    words = input_str.split()
    for word in words:
        clean_word = re.sub(r'[^A-Z0-9]', '', word.upper())
        if 1 <= len(clean_word) <= 5 and clean_word.isalnum():
            return clean_word
    
    return None


def get_workspace_root() -> Path:
    """
    Find the workspace root (contains .github/skills/)
    """
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / '.github' / 'skills').exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find workspace root")


def call_tavily_research(ticker: str, company_name: Optional[str], sector: Optional[str]) -> Tuple[bool, str]:
    """
    Call the tavily-research script and wait for web-search.json to be generated.
    
    Returns: (success: bool, json_path or error_message: str)
    """
    workspace_root = get_workspace_root()
    script_path = workspace_root / '.github' / 'skills' / 'tavily-research' / 'scripts' / 'researcher.py'
    output_path = workspace_root / 'evaluaciones' / ticker / 'raw-search' / 'web-search.json'
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    try:
        print(f"[1/2] Generating Tavily research for {ticker}...")
        
        # Build command
        cmd = [sys.executable, str(script_path), '--ticker', ticker]
        if company_name:
            cmd.extend(['--company-name', company_name])
        if sector:
            cmd.extend(['--sector', sector])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return False, f"tavily-research error: {result.stderr}"
        
        # Wait for file to be created (max 30 seconds)
        for attempt in range(30):
            if output_path.exists():
                print(f"   OK Research completed: {output_path}")
                return True, str(output_path)
            time.sleep(1)
        
        return False, f"web-search.json not generated: {output_path}"
    
    except subprocess.TimeoutExpired:
        return False, f"Timeout executing tavily-research for {ticker}"
    except Exception as e:
        return False, f"Error executing tavily-research: {str(e)}"


def call_web_search_fundamentales(json_path: str) -> Tuple[bool, str]:
    """
    Call the web-search-fundamentales script to convert JSON to markdown.
    
    Args:
        json_path: Path to the generated web-search.json file
    
    Returns: (success: bool, md_path or error_message: str)
    """
    workspace_root = get_workspace_root()
    script_path = workspace_root / '.github' / 'skills' / 'web-search-fundamentales' / 'scripts' / 'extract_fundamentales.py'
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    # Infer markdown output path from JSON path
    json_path_obj = Path(json_path)
    md_path = json_path_obj.parent.parent / 'informe-fundamentales.md'
    
    try:
        print(f"[2/2] Generating fundamentals report...")
        
        result = subprocess.run(
            [sys.executable, str(script_path), json_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return False, f"web-search-fundamentales error: {result.stderr}"
        
        # Verify markdown was created
        for attempt in range(10):
            if md_path.exists():
                print(f"   OK Fundamentals report generated: {md_path}")
                return True, str(md_path)
            time.sleep(0.5)
        
        return False, f"informe-fundamentales.md not generated: {md_path}"
    
    except subprocess.TimeoutExpired:
        return False, f"Timeout executing web-search-fundamentales"
    except Exception as e:
        return False, f"Error executing web-search-fundamentales: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Mini-workflow: Tavily Research → Web Search Fundamentales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_workflow.py --ticker REP.MC
  python run_workflow.py --ticker REP.MC --company-name "Repsol, S.A." --sector "Energy / Oil & Gas"
  python run_workflow.py --from-natural "investigar Apple Inc (AAPL)"
        """
    )
    
    parser.add_argument('--ticker', help='Stock ticker symbol (e.g., REP.MC, AAPL)')
    parser.add_argument('--company-name', help='Full company name (optional)')
    parser.add_argument('--sector', help='Industry sector (optional)')
    parser.add_argument('--from-natural', help='Extract ticker from natural language input')
    
    args = parser.parse_args()
    
    # Determine ticker
    if args.from_natural:
        ticker = extract_ticker(args.from_natural)
        if not ticker:
            print(f"ERROR Could not extract valid ticker from: {args.from_natural}")
            return 1
    elif args.ticker:
        ticker = extract_ticker(args.ticker)
        if not ticker:
            print(f"ERROR Invalid ticker: {args.ticker}")
            return 1
    else:
        parser.print_help()
        return 1
    
    print(f"\n Starting research workflow for ticker: {ticker}\n")
    
    # Step 1: Tavily Research
    success, result = call_tavily_research(ticker, args.company_name, args.sector)
    if not success:
        print(f"ERROR {result}")
        return 1
    
    json_path = result
    
    # Step 2: Web Search Fundamentales
    success, result = call_web_search_fundamentales(json_path)
    if not success:
        print(f"ERROR {result}")
        return 1
    
    md_path = result
    
    # Success
    print(f"\nCOMPLETADO Workflow completed successfully for {ticker}")
    print(f"\nArchivos generados: Generated files:")
    print(f"   • Research JSON: {json_path}")
    print(f"   • Fundamentals Report: {md_path}")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
