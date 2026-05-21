"""Report service - handles reading reports and metrics."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import sys

from app.config import REPORTS_DIR
from app.models import MetricsData


def generate_metrics_if_missing(ticker: str) -> bool:
    """
    Automatically generate metrics if they don't exist but the report does.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        True if metrics were generated or already exist, False otherwise
    """
    metrics_path = REPORTS_DIR / ticker / "raw-search" / "metrics.json"
    
    # Metrics already exist
    if metrics_path.exists():
        return True
    
    # Check if report exists (metrics should exist if report does)
    report_path = REPORTS_DIR / ticker / "informe-final.md"
    if not report_path.exists():
        return False
    
    # Report exists but metrics don't - generate them
    try:
        from app.services.generation_service import generate_metrics
        print(f"Auto-generating metrics for {ticker}...")
        # Launch generation in background to keep response fast
        return generate_metrics(ticker, background=True)
    except Exception as e:
        print(f"Error auto-generating metrics: {e}")
        return False


def get_report_status(ticker: str) -> dict:
    """Check if a final report exists and return metadata."""
    report_path = REPORTS_DIR / ticker / "informe-final.md"
    
    if not report_path.exists():
        return {"exists": False}
    
    # Get file modification time
    mod_time = report_path.stat().st_mtime
    mod_datetime = datetime.fromtimestamp(mod_time)
    age_days = (datetime.now() - mod_datetime).days
    
    return {
        "exists": True,
        "age_days": age_days,
        "generated_date": mod_datetime.strftime("%Y-%m-%d")
    }


def load_metrics_json(ticker: str) -> Optional[MetricsData]:
    """Load metrics JSON if it exists."""
    metrics_path = REPORTS_DIR / ticker / "raw-search" / "metrics.json"
    
    if not metrics_path.exists():
        return None
    
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return MetricsData(**data)
    except Exception as e:
        print(f"Error loading metrics for {ticker}: {e}")
        return None


def get_report_content(ticker: str) -> Optional[str]:
    """Load the full report markdown."""
    report_path = REPORTS_DIR / ticker / "informe-final.md"
    
    if not report_path.exists():
        # Try technical report as fallback
        report_path = REPORTS_DIR / ticker / "informe-tecnico.md"
    
    if not report_path.exists():
        return None
    
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading report for {ticker}: {e}")
        return None


def get_report_data(ticker: str) -> Optional[dict]:
    """Get combined report data (content + metrics + metadata).
    
    Automatically generates metrics if report exists but metrics don't.
    """
    report_content = get_report_content(ticker)
    if not report_content:
        return None
    
    # Ensure metrics exist (auto-generate if missing)
    generate_metrics_if_missing(ticker)
    
    status = get_report_status(ticker)
    metrics = load_metrics_json(ticker)
    
    return {
        "content": report_content,
        "ticker": ticker,
        "generated_date": status.get("generated_date"),
        "metrics": metrics.model_dump() if metrics else None
    }


def get_price_history(ticker: str) -> Optional[list]:
    """Extract price history from metrics JSON for CSV export."""
    metrics = load_metrics_json(ticker)
    if not metrics or not metrics.precios_historicos:
        return None
    
    # Get the longest available history
    history = (
        metrics.precios_historicos.get("ultimos_12m") or
        metrics.precios_historicos.get("ultimos_6m") or
        []
    )
    
    return history
