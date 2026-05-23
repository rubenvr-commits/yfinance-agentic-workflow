#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

import importlib


def test_check_env_missing(monkeypatch):
    # Ensure env vars are not present
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("YFINANCE_API_KEY", raising=False)

    # Reload module to run top-level main only when invoked
    module = importlib.import_module("check_env")

    try:
        # Calling main should exit with SystemExit(1)
        module.main()
        assert False, "Expected SystemExit due to missing env vars"
    except SystemExit as e:
        assert e.code == 1


def test_check_env_present(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "x")
    monkeypatch.setenv("YFINANCE_API_KEY", "y")

    module = importlib.import_module("check_env")

    # Should exit 0 or simply return without raising
    # module.main uses sys.exit(1) only on missing, so calling should not raise
    module.main()
