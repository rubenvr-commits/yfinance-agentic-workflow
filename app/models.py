"""Pydantic models for API responses."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ReportStatus(BaseModel):
    """Report status response."""
    exists: bool
    age_days: Optional[int] = None
    generated_date: Optional[str] = None


class MetricsData(BaseModel):
    """Financial metrics data."""
    ticker: str
    fecha: str
    precio_actual: Optional[float] = None
    precios_historicos: Optional[Dict[str, List[Dict[str, Any]]]] = None
    valuations: Optional[Dict[str, Optional[float]]] = None
    performance: Optional[Dict[str, Optional[float]]] = None
    sector_comparison: Optional[Dict[str, Optional[float]]] = None


class ReportResponse(BaseModel):
    """Full report response."""
    content: str
    ticker: str
    generated_date: Optional[str] = None
    metrics: Optional[MetricsData] = None


class GenerationStatus(BaseModel):
    """Report generation status."""
    status: str  # "started", "in_progress", "completed", "error"
    phases: List[str] = ["tecnico", "fundamentales", "berkshire", "final"]
    current_phase: Optional[str] = None
    progress_percent: int = 0
    message: Optional[str] = None


class GenerationResult(BaseModel):
    """Final generation result."""
    status: str
    ticker: str
    url: Optional[str] = None
    message: Optional[str] = None
