#!/usr/bin/env python3
"""
Pre-commit validator hook: Checks if code changes have corresponding tests before allowing commits.
Receives tool invocation JSON from agent PreToolUse hook.
"""

import json
import sys
import subprocess
from pathlib import Path

def get_staged_files():
    """Get list of staged files ready for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        print(f"Warning: Could not get staged files: {e}")
        return []

def has_corresponding_tests(py_file):
    """Check if a Python file has corresponding test file."""
    file_path = Path(py_file)
    
    test_locations = [
        Path("tests") / f"test_{file_path.name}",
        Path("__tests__") / f"{file_path.stem}.test.py",
        file_path.parent / f"test_{file_path.name}",
        file_path.parent / f"{file_path.stem}_test.py",
    ]
    
    for test_file in test_locations:
        if test_file.exists():
            return str(test_file)
    
    return None

def validate_commit():
    """Main validation logic."""
    staged_files = get_staged_files()
    py_files = [f for f in staged_files if f.endswith(".py") and f and not f.startswith("tests/") and not f.startswith(".github/scripts/")]
    
    if not py_files:
        # No Python files, allow commit
        return {"continue": True}
    
    # Check for test files
    missing_tests = []
    for py_file in py_files:
        # Skip test files and infrastructure scripts
        if "test" in py_file or "__pycache__" in py_file or "validate_" in py_file or py_file.startswith("run_"):
            continue
        
        if not has_corresponding_tests(py_file):
            missing_tests.append(py_file)
    
    if missing_tests:
        # Ask user if they want to run tests
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"No tests found for: {', '.join(missing_tests[:3])}. Run Q&A Tester to validate changes before committing?"
            }
        }
    
    return {"continue": True}

if __name__ == "__main__":
    try:
        # Read hook input from stdin (if available)
        hook_input = sys.stdin.read() if not sys.stdin.isatty() else "{}"
        
        # Validate commit
        result = validate_commit()
        
        # Output result as JSON
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        # Non-blocking warning
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "warning": f"Pre-commit validator error: {e}"
            }
        }))
        sys.exit(0)
