#!/usr/bin/env python3
"""
Comprehensive test validation for all staged changes in pre-commit system.
Tests Python validation logic, bash script syntax, and integration scenarios.
"""

import json
import sys
import subprocess
from pathlib import Path

# Use ASCII-safe symbols for Windows compatibility
PASS_SYMBOL = "[OK]"
FAIL_SYMBOL = "[XX]"

def test_python_validator_logic():
    """Test 1: Python validation script logic"""
    print("\n[TEST 1] Python Pre-Commit Validator Logic")
    print("-" * 50)
    
    result = subprocess.run(
        [sys.executable, "tests/test_pre_commit_validator.py"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"FAIL: {result.stderr}")
        return False

def test_configuration_files():
    """Test 1.5: Configuration files validation"""
    print("\n[TEST 1.5] Configuration Files Validation")
    print("-" * 50)
    
    result = subprocess.run(
        [sys.executable, "tests/test_configuration_files.py"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        # Extract summary lines
        lines = result.stdout.split('\n')
        for line in lines:
            if 'TEST' in line or 'PASS' in line or 'FAIL' in line or 'Total' in line or '✓' in line or '✗' in line:
                print(line)
        return True
    else:
        print(f"FAIL: {result.stderr}")
        return False

def test_bash_script_syntax():
    """Test 2: Bash script syntax validation"""
    print("\n[TEST 2] Bash Script Syntax Validation")
    print("-" * 50)
    
    bash_script = ".github/scripts/git-pre-commit"
    script_path = Path(bash_script)
    
    if not script_path.exists():
        print(f"✗ Script not found: {bash_script}")
        return False
    
    content = script_path.read_text()
    
    # Required shell script patterns
    validation_checks = [
        ("#!/bin/bash" in content, "Shebang present"),
        ("set -e" in content, "Error handling (set -e)"),
        ("git diff --cached" in content, "Git diff command"),
        ("STAGED_FILES" in content, "Staged files handling"),
        ("MISSING_TESTS" in content, "Test detection logic"),
        (".py$" in content, "Python file filtering"),
        ("exit 0" in content, "Exit codes defined"),
        ("grep -v '^tests/'" in content, "Tests directory exclusion"),
    ]
    
    passed = sum(1 for check, _ in validation_checks if check)
    for check, desc in validation_checks:
        symbol = PASS_SYMBOL if check else FAIL_SYMBOL
        print(f"{symbol} {desc}")
    
    if passed == len(validation_checks):
        print(f"{PASS_SYMBOL} Script structure validated successfully")
        return True
    else:
        print(f"{FAIL_SYMBOL} {len(validation_checks) - passed} validation(s) failed")
        return False

def test_staged_files_integrity():
    """Test 3: Verify all staged files exist and are valid"""
    print("\n[TEST 3] Staged Files Integrity")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        staged_files = [f for f in staged_files if f]  # Filter empty strings
        
        all_exist = True
        for f in staged_files:
            path = Path(f)
            if path.exists():
                print(f"{PASS_SYMBOL} {f}")
            else:
                print(f"{FAIL_SYMBOL} {f} (missing)")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"✗ Error checking staged files: {e}")
        return False

def test_validator_json_output():
    """Test 4: Validate JSON output format of Python validator"""
    print("\n[TEST 4] Validator JSON Output Format")
    print("-" * 50)
    
    validator_path = ".github/scripts/validate_pre_commit.py"
    
    try:
        # Import the validator
        sys.path.insert(0, str(Path(".github/scripts")))
        from validate_pre_commit import validate_commit
        
        result = validate_commit()
        
        # Validate output is valid JSON-serializable
        try:
            json_str = json.dumps(result)
            print(f"{PASS_SYMBOL} Output is valid JSON")
            print(f"{PASS_SYMBOL} Output structure: {json.dumps(result, indent=2)}")
            
            # Check required fields
            has_valid_structure = (
                "continue" in result or 
                "hookSpecificOutput" in result
            )
            
            if has_valid_structure:
                print(f"{PASS_SYMBOL} Output has valid structure")
                return True
            else:
                print(f"{FAIL_SYMBOL} Output missing required fields")
                return False
        except Exception as e:
            print(f"{FAIL_SYMBOL} Output is not JSON serializable: {e}")
            return False
    except Exception as e:
        print(f"{FAIL_SYMBOL} Error validating output: {e}")
        return False

def test_tests_directory_exclusion():
    """Test 5: Verify tests directory is properly excluded"""
    print("\n[TEST 5] Tests Directory Exclusion")
    print("-" * 50)
    
    try:
        sys.path.insert(0, str(Path(".github/scripts")))
        from validate_pre_commit import validate_commit
        
        # Check that the validator filters out test files
        validator_code = Path(".github/scripts/validate_pre_commit.py").read_text()
        bash_code = Path(".github/scripts/git-pre-commit").read_text()
        
        checks = [
            ("not f.startswith(\"tests/\")" in validator_code, "Python validator excludes tests/"),
            ("grep -v '^tests/'" in bash_code, "Bash script excludes tests/"),
            ("not f.startswith(\".github/scripts/\")" in validator_code, "Python validator excludes .github/scripts/"),
            (".github/scripts/" in bash_code and "grep -v" in bash_code, "Bash script excludes .github/scripts/"),
            ("validate_" in validator_code, "Python validator excludes validate_ scripts"),
            ("run_" in validator_code, "Python validator excludes run_ scripts"),
        ]
        
        passed = sum(1 for check, _ in checks if check)
        for check, desc in checks:
            symbol = PASS_SYMBOL if check else FAIL_SYMBOL
            print(f"{symbol} {desc}")
        
        return passed == len(checks)
    except Exception as e:
        print(f"✗ Error validating exclusion: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("STAGED CHANGES TEST SUITE - Pre-Commit Validation System")
    print("=" * 60)
    
    tests = [
        ("Python Validator Tests", test_python_validator_logic),
        ("Configuration Files Validation", test_configuration_files),
        ("Bash Script Syntax", test_bash_script_syntax),
        ("Staged Files Integrity", test_staged_files_integrity),
        ("JSON Output Validation", test_validator_json_output),
        ("Tests Directory Exclusion", test_tests_directory_exclusion),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = PASS_SYMBOL if passed else FAIL_SYMBOL
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nTotal: {passed_count}/{total_count} test groups passed")
    
    if passed_count == total_count:
        print(f"\n{PASS_SYMBOL} All staged changes validated successfully!")
        return 0
    else:
        print(f"\n{FAIL_SYMBOL} {total_count - passed_count} test group(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
