"""Generation service - handles report generation workflow."""

import subprocess
import json
from pathlib import Path
from typing import Optional
import asyncio

from app.config import BASE_DIR


async def trigger_generation(ticker: str) -> dict:
    """
    Trigger the financial report generation workflow.
    Currently returns a placeholder status.
    In Phase 2, this would integrate with the actual agent.
    """
    
    # Validate ticker format
    if not ticker or not all(c.isalnum() or c == '.' for c in ticker):
        return {
            "status": "error",
            "message": f"Invalid ticker format: {ticker}"
        }
    
    ticker = ticker.upper()
    
    # For Phase 1, we'll use a simple workflow simulation
    # In Phase 2, this would call the actual analista-financiero agent
    
    return {
        "status": "started",
        "ticker": ticker,
        "phases": ["tecnico", "fundamentales", "berkshire", "final"],
        "current_phase": "tecnico",
        "progress_percent": 0,
        "message": "Report generation initiated"
    }


async def get_generation_progress(ticker: str) -> dict:
    """Get current generation progress (placeholder for Phase 1)."""
    
    return {
        "status": "in_progress",
        "ticker": ticker,
        "current_phase": "fundamentales",
        "progress_percent": 33,
        "message": "Processing fundamental analysis"
    }


async def check_generation_complete(ticker: str) -> Optional[dict]:
    """Check if generation is complete."""
    
    report_path = Path("evaluaciones") / ticker / "informe-final.md"
    if report_path.exists():
        return {
            "status": "completed",
            "ticker": ticker,
            "url": f"/report/{ticker}"
        }
    
    return None
