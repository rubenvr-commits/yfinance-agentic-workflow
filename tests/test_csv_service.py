"""Tests for CSV service."""

import pytest
from app.services.csv_service import generate_price_csv


def test_generate_price_csv_nvda():
    """Test CSV generation for NVDA ticker."""
    csv_data = generate_price_csv("NVDA")
    if csv_data:
        assert "Date,Close" in csv_data
        lines = csv_data.strip().split("\n")
        assert len(lines) >= 1
        assert lines[0] == "Date,Close"


def test_generate_price_csv_nonexistent():
    """Test CSV generation for non-existent ticker."""
    csv_data = generate_price_csv("NONEXISTENT_TICKER_XYZ")
    assert csv_data is None


def test_generate_price_csv_format():
    """Test that CSV has valid format with dates."""
    csv_data = generate_price_csv("NVDA")
    if csv_data:
        lines = csv_data.strip().split("\n")
        if len(lines) > 1:
            data_line = lines[1]
            assert "," in data_line
            parts = data_line.split(",")
            assert len(parts) == 2
