"""Tests for Pydantic models."""

import pytest
from app.models import (
    ReportStatus, MetricsData, ReportResponse,
    GenerationStatus, GenerationResult
)


def test_report_status_model():
    """Test ReportStatus model creation and validation."""
    status = ReportStatus(exists=True, age_days=5, generated_date="2026-05-16")
    assert status.exists is True
    assert status.age_days == 5
    assert status.generated_date == "2026-05-16"


def test_report_status_not_exists():
    """Test ReportStatus when report doesn't exist."""
    status = ReportStatus(exists=False)
    assert status.exists is False
    assert status.age_days is None


def test_metrics_data_model():
    """Test MetricsData model creation."""
    metrics = MetricsData(
        ticker="NVDA",
        fecha="2026-05-21",
        precio_actual=875.50
    )
    assert metrics.ticker == "NVDA"
    assert metrics.precio_actual == 875.50


def test_generation_status_model():
    """Test GenerationStatus model."""
    status = GenerationStatus(
        status="started",
        current_phase="tecnico",
        progress_percent=0
    )
    assert status.status == "started"
    assert status.current_phase == "tecnico"
    assert status.progress_percent == 0
    assert len(status.phases) == 4


def test_report_response_model():
    """Test ReportResponse model with optional metrics."""
    response = ReportResponse(
        content="# Report",
        ticker="NVDA",
        generated_date="2026-05-21"
    )
    assert response.ticker == "NVDA"
    assert response.content == "# Report"
