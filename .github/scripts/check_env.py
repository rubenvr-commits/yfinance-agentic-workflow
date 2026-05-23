#!/usr/bin/env python3
"""Check required environment variables for CI runs.

Exits with code 0 if all present, 1 otherwise. Prints JSON with details.
"""
import os
import json
import sys
from pathlib import Path

REQUIRED = [
    "TAVILY_API_KEY",
    "YFINANCE_API_KEY"
]

def main():
    missing = []
    present = {}
    for name in REQUIRED:
        val = os.getenv(name)
        present[name] = bool(val)
        if not val:
            missing.append(name)

    out = {
        "all_present": len(missing) == 0,
        "missing": missing,
        "present": present
    }

    print(json.dumps(out, indent=2))
    if missing:
        sys.exit(1)

if __name__ == "__main__":
    main()
