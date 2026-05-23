"""Backend service helpers for the Analista Financiero watcher."""

import os
import subprocess
import sys
from pathlib import Path

from app.config import RUN_ANALISTA_AGENT


BASE_DIR = Path(__file__).resolve().parents[2]
ANALISTA_AGENT_SCRIPT = BASE_DIR / ".github" / "scripts" / "run_analista_agent.py"

_analista_agent_process: subprocess.Popen | None = None


def start_analista_agent() -> None:
    """Start the background watcher if it is enabled and available."""
    global _analista_agent_process

    if not RUN_ANALISTA_AGENT:
        return

    if os.environ.get("PYTEST_CURRENT_TEST"):
        return

    if _analista_agent_process and _analista_agent_process.poll() is None:
        return

    if not ANALISTA_AGENT_SCRIPT.exists():
        print(f"Analista Financiero agent not found at {ANALISTA_AGENT_SCRIPT}")
        return

    print("Starting Analista Financiero agent...")
    _analista_agent_process = subprocess.Popen(
        [sys.executable, str(ANALISTA_AGENT_SCRIPT)],
        cwd=str(BASE_DIR),
    )


def stop_analista_agent() -> None:
    """Stop the background watcher if it is running."""
    global _analista_agent_process

    if not _analista_agent_process or _analista_agent_process.poll() is not None:
        return

    print("Stopping Analista Financiero agent...")
    _analista_agent_process.terminate()
    try:
        _analista_agent_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _analista_agent_process.kill()
        _analista_agent_process.wait(timeout=10)

    _analista_agent_process = None