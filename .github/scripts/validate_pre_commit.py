#!/usr/bin/env python3
"""
Pre-commit validator hook: Checks if code changes have corresponding tests before allowing commits.
Receives tool invocation JSON from agent PreToolUse hook.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import os

def get_staged_files():
    """Get list of staged files ready for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=30
        )
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        repo_root = Path.cwd()
        normalized = []
        for f in (f.strip() for f in files if f and f.strip()):
            try:
                p = (repo_root / f).resolve()
                # store relative posix path
                normalized.append(str(p.relative_to(repo_root).as_posix()))
            except Exception:
                normalized.append(f.replace('\\','/'))
        return normalized
    except Exception as e:
        print(f"Warning: Could not get staged files: {e}")
        return []

def has_corresponding_tests(py_file):
    """Check if a Python file has corresponding test file."""
    repo_root = Path.cwd()
    file_path = Path(py_file)
    stem = file_path.stem

    test_locations = [
        repo_root / "tests" / f"test_{stem}.py",
        repo_root / "__tests__" / f"{stem}.test.py",
        (repo_root / file_path.parent) / f"test_{stem}.py",
        (repo_root / file_path.parent) / f"{stem}_test.py",
    ]

    for test_file in test_locations:
        if test_file.exists():
            return str(test_file.relative_to(repo_root))

    return None

def validate_commit():
    """Main validation logic."""
    staged_files = get_staged_files()
    py_files = []
    for f in staged_files:
        try:
            p = Path(f)
        except Exception:
            continue

        # Only python files
        if p.suffix != ".py":
            continue

        parts = [part for part in p.parts]
        # Exclude files under any tests/ folder or under top-level .github/scripts/
        if "tests" in parts:
            continue
        if len(parts) >= 2 and parts[0] == ".github" and parts[1] == "scripts":
            continue

        py_files.append(str(p))
    
    if not py_files:
        # No Python files, allow commit
        return {"continue": True}
    
    # Check for test files
    missing_tests = []
    for py_file in py_files:
        # Skip test files and infrastructure scripts
        p = Path(py_file)
        if "test" in p.name or "__pycache__" in p.parts or p.name.startswith("validate_") or p.name.startswith("run_"):
            continue

        if not has_corresponding_tests(py_file):
            missing_tests.append(py_file)
    
    # Prepare structured log for auditing
    logs_dir = Path(".github/hooks/logs/pre_commit_validator")
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    safe_ts = timestamp.replace(":", "_")
    log_file = logs_dir / f"run_{safe_ts}.json"
    log_payload = {
        "timestamp": timestamp,
        "staged_files": staged_files,
        "py_files": py_files,
        "missing_tests": missing_tests,
    }
    try:
        log_file.write_text(json.dumps(log_payload, indent=2))
    except Exception:
        # non-fatal
        pass

    if missing_tests:
        # Ask user if they want to run tests
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"No tests found for: {', '.join(missing_tests[:3])}. Run Q&A Tester to validate changes before committing?"
            },
            "transcript_path": str(log_file)
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
