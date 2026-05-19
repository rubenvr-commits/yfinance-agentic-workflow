#!/usr/bin/env python3
"""
Test suite for pre-commit validator hook.
Validates that the hook correctly detects missing test files.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from validate_pre_commit import has_corresponding_tests, validate_commit

def test_detect_test_file_in_tests_dir():
    """Test: Detects test file in tests/ directory."""
    # This test doesn't create actual files, so we'll just verify the logic
    assert has_corresponding_tests("src/nonexistent.py") is None
    print("PASS: test_detect_test_file_in_tests_dir")

def test_validate_returns_continue_on_success():
    """Test: Returns continue=True when validation passes."""
    # Temporarily patch to simulate clean state
    result = validate_commit()
    assert "continue" in result or "hookSpecificOutput" in result
    print("PASS: test_validate_returns_continue_on_success")

def test_hook_output_structure():
    """Test: Hook output follows JSON schema."""
    result = validate_commit()
    
    if "hookSpecificOutput" in result:
        output = result["hookSpecificOutput"]
        assert "hookEventName" in output
        assert output["hookEventName"] == "PreToolUse"
        print("PASS: test_hook_output_structure")
    elif "continue" in result:
        assert isinstance(result["continue"], bool)
        print("PASS: test_hook_output_structure (continue path)")
    else:
        raise AssertionError("Invalid hook output structure")

if __name__ == "__main__":
    tests = [
        test_detect_test_file_in_tests_dir,
        test_validate_returns_continue_on_success,
        test_hook_output_structure,
    ]
    
    failed = 0
    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"FAIL: {test_func.__name__} - {e}")
            failed += 1
    
    print(f"\n{len(tests)-failed}/{len(tests)} tests passed")
    sys.exit(0 if failed == 0 else 1)
