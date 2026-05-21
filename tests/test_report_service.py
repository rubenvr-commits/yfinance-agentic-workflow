"""Tests for report service."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.report_service import (
    get_report_status, load_metrics_json, get_report_content,
    get_report_data, get_price_history
)
from app.config import REPORTS_DIR


def test_get_report_status_not_exists():
    """Test get_report_status when report doesn't exist."""
    status = get_report_status("NONEXISTENT")
    assert status["exists"] is False


def test_get_report_status_exists():
    """Test get_report_status when report exists."""
    status = get_report_status("NVDA")
    if status["exists"]:
        assert "age_days" in status
        assert "generated_date" in status
        assert isinstance(status["age_days"], int)


def test_load_metrics_json_nvda():
    """Test loading metrics JSON for existing ticker."""
    metrics = load_metrics_json("NVDA")
    if metrics:
        assert metrics.ticker == "NVDA"
        assert metrics.fecha is not None


def test_load_metrics_json_nonexistent():
    """Test loading metrics JSON for non-existent ticker."""
    metrics = load_metrics_json("NONEXISTENT_TICKER_XYZ")
    assert metrics is None


def test_get_report_content_exists():
    """Test getting report content for existing ticker."""
    content = get_report_content("NVDA")
    if content:
        assert isinstance(content, str)
        assert len(content) > 0


def test_get_report_content_nonexistent():
    """Test getting report content for non-existent ticker."""
    content = get_report_content("NONEXISTENT_TICKER_XYZ")
    assert content is None


def test_get_report_data_complete():
    """Test getting complete report data."""
    data = get_report_data("NVDA")
    if data:
        assert "ticker" in data
        assert "content" in data
        assert data["ticker"] == "NVDA"


def test_get_price_history_nvda():
    """Test extracting price history for NVDA."""
    history = get_price_history("NVDA")
    if history:
        assert isinstance(history, list)
        if len(history) > 0:
            assert "date" in history[0]
            assert "close" in history[0]
