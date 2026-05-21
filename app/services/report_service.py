"""Report service - handles reading reports and metrics."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from app.config import REPORTS_DIR
from app.models import MetricsData


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
    """Get combined report data (content + metrics + metadata)."""
    report_content = get_report_content(ticker)
    if not report_content:
        return None
    
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
