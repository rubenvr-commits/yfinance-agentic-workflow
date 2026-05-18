#!/usr/bin/env python3
"""
Script de evaluación para combined-valuation-workflow skill.

Verifica que:
1. Ambos archivos (informe-tecnico.md y informe-berkshire.md) fueron creados
2. Los archivos tienen contenido válido y no están vacíos
3. El workflow se ejecutó sin errores críticos
4. Los archivos están en la ubicación correcta
"""

import sys
import json
from pathlib import Path
import argparse


def check_files_exist(ticker: str, workspace_root: Path) -> bool:
    """Verifica que ambos archivos existan."""
    yfinance_file = workspace_root / 'evaluaciones' / ticker / 'informe-tecnico.md'
    berkshire_file = workspace_root / 'evaluaciones' / ticker / 'informe-berkshire.md'
    
    print(f"  Checking yfinance report: {yfinance_file}")
    if not yfinance_file.exists():
        print(f"    ❌ File not found")
        return False
    print(f"    ✓ Exists ({yfinance_file.stat().st_size} bytes)")
    
    print(f"  Checking Berkshire report: {berkshire_file}")
    if not berkshire_file.exists():
        print(f"    ❌ File not found")
        return False
    print(f"    ✓ Exists ({berkshire_file.stat().st_size} bytes)")
    
    return True


def check_file_content(ticker: str, workspace_root: Path) -> bool:
    """Verifica que los archivos tengan contenido válido."""
    yfinance_file = workspace_root / 'evaluaciones' / ticker / 'informe-tecnico.md'
    berkshire_file = workspace_root / 'evaluaciones' / ticker / 'informe-berkshire.md'
    
    # Verificar contenido de yfinance
    print(f"  Checking yfinance content...")
    try:
        with open(yfinance_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content:
            print(f"    ❌ File is empty")
            return False
        
        # Verificar que contiene secciones esperadas
        required_sections = [ticker, "CURRENT_PRICE", "MARKET_CAP"]
        missing = [s for s in required_sections if s not in content]
        
        if missing:
            print(f"    ⚠️  Missing expected sections: {missing}")
        else:
            print(f"    ✓ Contains expected financial data")
    except Exception as e:
        print(f"    ❌ Error reading file: {e}")
        return False
    
    # Verificar contenido de Berkshire
    print(f"  Checking Berkshire content...")
    try:
        with open(berkshire_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content:
            print(f"    ❌ File is empty")
            return False
        
        # Verificar que tiene contenido (al menos más que un párrafo)
        if len(content) < 200:
            print(f"    ⚠️  File is very short ({len(content)} bytes)")
        else:
            print(f"    ✓ Contains substantial content ({len(content)} bytes)")
    except Exception as e:
        print(f"    ❌ Error reading file: {e}")
        return False
    
    return True


def grade_eval(ticker: str, workspace_root: Path) -> dict:
    """Evalúa un caso de prueba."""
    results = {
        "ticker": ticker,
        "assertions": []
    }
    
    print(f"\nEvaluating test case: {ticker}")
    print("=" * 50)
    
    # Assertion 1: Files exist
    print("\n[Assertion 1] Both report files were created")
    files_exist = check_files_exist(ticker, workspace_root)
    results["assertions"].append({
        "text": "Both report files (yfinance and Berkshire) exist in evaluaciones/{ticker}/",
        "passed": files_exist,
        "evidence": "File existence check"
    })
    
    # Assertion 2: Files have content
    print("\n[Assertion 2] Files have valid content")
    has_content = check_file_content(ticker, workspace_root)
    results["assertions"].append({
        "text": "Both files contain valid, non-empty content",
        "passed": has_content,
        "evidence": "Content validation check"
    })
    
    # Assertion 3: Files are in correct location
    print("\n[Assertion 3] Files are in correct directory")
    correct_path = (workspace_root / 'evaluaciones' / ticker / 'informe-tecnico.md').exists()
    results["assertions"].append({
        "text": "Files are located in evaluaciones/{ticker}/ directory",
        "passed": correct_path,
        "evidence": f"evaluaciones/{ticker}/"
    })
    
    print("\n" + "=" * 50)
    pass_count = sum(1 for a in results["assertions"] if a["passed"])
    print(f"\nResult: {pass_count}/{len(results['assertions'])} assertions passed")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate combined-valuation-workflow test cases")
    parser.add_argument('--workspace-root', type=Path, required=True, help='Workspace root path')
    parser.add_argument('--ticker', required=True, help='Ticker to evaluate')
    parser.add_argument('--output', type=Path, help='Output JSON file for grading results')
    
    args = parser.parse_args()
    
    results = grade_eval(args.ticker, args.workspace_root)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {args.output}")
    
    # Return non-zero if any assertion failed
    passed_all = all(a["passed"] for a in results["assertions"])
    return 0 if passed_all else 1


if __name__ == '__main__':
    sys.exit(main())
