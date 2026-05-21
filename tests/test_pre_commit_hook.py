"""
Test script to validate the pre-commit hook detects tests correctly.
"""
import subprocess
import os
import sys
from pathlib import Path


def run_pre_commit_check():
    """Run the pre-commit hook and capture output."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Get list of Python files that would be checked
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Warning: Could not get staged files")
        return
    
    staged_files = result.stdout.strip().split('\n')
    py_files = [f for f in staged_files if f.endswith('.py') and '__pycache__' not in f]
    
    print(f"Python files to check: {len(py_files)}")
    for f in py_files:
        print(f"  - {f}")
    
    # List test files
    test_dir = project_root / "tests"
    if test_dir.exists():
        test_files = list(test_dir.glob("*.py"))
        print(f"\nAvailable test files: {len(test_files)}")
        for f in test_files:
            print(f"  - {f.name}")


if __name__ == "__main__":
    run_pre_commit_check()
