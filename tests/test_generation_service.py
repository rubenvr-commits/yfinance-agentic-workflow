"""Tests for generation service."""

import pytest
import asyncio

from app.services.generation_service import (
    trigger_generation, get_generation_progress, check_generation_complete,
    build_agent_request_payload,
)


@pytest.mark.asyncio
async def test_trigger_generation_valid_ticker():
    """Test triggering generation with valid ticker."""
    result = await trigger_generation("NVDA")
    assert result["status"] == "started"
    assert result["ticker"] == "NVDA"
    assert "phases" in result


@pytest.mark.asyncio
async def test_trigger_generation_invalid_ticker():
    """Test triggering generation with invalid ticker format."""
    result = await trigger_generation("INVALID@#$")
    assert result["status"] == "error"
    assert "Invalid" in result.get("message", "")


@pytest.mark.asyncio
async def test_trigger_generation_lowercase_uppercase():
    """Test that ticker is normalized to uppercase."""
    result = await trigger_generation("nvda")
    assert result["ticker"] == "NVDA"


def test_build_agent_request_payload_sets_todo_status():
    """Test that new agent requests are queued with to do status."""
    payload = build_agent_request_payload("NVDA", 60)
    assert payload["ticker"] == "NVDA"
    assert payload["status"] == "to do"
    assert payload["requested_by"] == "web_ui"


@pytest.mark.asyncio
async def test_get_generation_progress():
    """Test getting generation progress."""
    progress = await get_generation_progress("NVDA")
    assert progress["status"] == "in_progress"
    assert progress["current_phase"] in ["tecnico", "fundamentales", "berkshire", "final"]
    assert 0 <= progress["progress_percent"] <= 100


@pytest.mark.asyncio
async def test_check_generation_complete():
    """Test checking if generation is complete."""
    result = await check_generation_complete("NVDA")
    if result:
        assert result["status"] == "completed"
        assert result["ticker"] == "NVDA"
