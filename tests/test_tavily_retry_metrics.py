import json
from unittest.mock import patch, Mock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "skills" / "tavily-research" / "scripts"))

from utils import TavilyAPIClient


def test_search_criterion_retries_and_metrics(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        # First two attempts: simulate 500, third attempt: success
        attempt = len(calls) + 1
        calls.append(attempt)
        mock = Mock()
        if attempt < 3:
            mock.status_code = 500
            mock.text = "Server error"
            return mock
        else:
            mock.status_code = 200
            mock.json.return_value = {"success": True, "results": [{"title": "r", "content": "c", "url": "u"}]}
            return mock

    monkeypatch.setattr("requests.post", fake_post)

    client = TavilyAPIClient(timeout=1)
    res = client.search_criterion("test query", max_results=1)

    assert res["status"] == "completed"
    assert "request_metrics" in res
    assert res["request_metrics"]["attempts"] == 3
