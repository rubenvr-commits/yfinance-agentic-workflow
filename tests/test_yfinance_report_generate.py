"""Unit tests for yfinance report generation script."""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock yfinance, pandas, numpy before importing generate_report
sys.modules['yfinance'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Add script path to import the module
script_path = Path(__file__).parent.parent / ".github" / "skills" / "yfinance-report" / "scripts"
if str(script_path) not in sys.path:
    sys.path.insert(0, str(script_path))

try:
    from generate_report import safe_get, format_currency, format_percentage, format_large_number
except (ImportError, Exception):
    pytest.skip("generate_report module not available", allow_module_level=True)


def test_safe_get_returns_value_when_present():
    """Test safe_get returns value when key exists and is not None."""
    test_dict = {"key": "value", "number": 42}
    assert safe_get(test_dict, "key") == "value"
    assert safe_get(test_dict, "number") == 42


def test_safe_get_returns_default_when_missing():
    """Test safe_get returns default value when key is missing or None."""
    test_dict = {"key": None}
    assert safe_get(test_dict, "missing") == "N/A"
    assert safe_get(test_dict, "key") == "N/A"


def test_format_currency_valid_number():
    """Test format_currency formats numbers correctly."""
    assert format_currency(1000) == "$1,000.00"
    assert format_currency(1000.50) == "$1,000.50"
    assert format_currency(1000, "EUR") == "EUR1,000.00"


def test_format_currency_invalid_input():
    """Test format_currency handles invalid input."""
    assert format_currency("N/A") == "N/A"
    assert format_currency(None) == "N/A"


def test_format_percentage_valid_number():
    """Test format_percentage formats numbers correctly."""
    assert format_percentage(5.5) == "5.50%"
    assert format_percentage(0.75) == "0.75%"


def test_format_percentage_invalid_input():
    """Test format_percentage handles invalid input."""
    assert format_percentage("N/A") == "N/A"
    assert format_percentage(None) == "N/A"


def test_format_large_number_valid_number():
    """Test format_large_number adds commas to numbers."""
    assert format_large_number(1000) == "1,000"
    assert format_large_number(1000000) == "1,000,000"


def test_format_large_number_invalid_input():
    """Test format_large_number handles invalid input."""
    assert format_large_number("N/A") == "N/A"
    assert format_large_number(None) == "N/A"
