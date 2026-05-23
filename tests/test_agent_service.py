"""Tests for the Analista Financiero backend watcher service."""

from types import SimpleNamespace

from app.services import agent_service


def test_start_analista_agent_respects_disable_flag(monkeypatch):
    """Test that the watcher does not start when the feature flag is disabled."""
    calls = []

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(agent_service, "RUN_ANALISTA_AGENT", False)
    monkeypatch.setattr(agent_service, "ANALISTA_AGENT_SCRIPT", SimpleNamespace(exists=lambda: True))
    monkeypatch.setattr(agent_service.subprocess, "Popen", lambda *args, **kwargs: calls.append((args, kwargs)))

    agent_service.start_analista_agent()

    assert calls == []