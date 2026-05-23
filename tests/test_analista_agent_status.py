"""Tests for analista-financiero request status handling."""

from importlib import util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "run_analista_agent.py"
SPEC = util.spec_from_file_location("run_analista_agent", SCRIPT_PATH)
run_analista_agent = util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(run_analista_agent)


def test_request_is_todo_only_accepts_todo():
    """Test that only 'to do' requests are accepted for processing."""
    assert run_analista_agent.request_is_todo({"status": "to do"}) is True
    assert run_analista_agent.request_is_todo({"status": "done"}) is False
    assert run_analista_agent.request_is_todo({}) is False


def test_mark_request_done_updates_status(tmp_path):
    """Test that a processed request is marked as done."""
    request_file = tmp_path / "agent-request.json"
    request_file.write_text('{"ticker": "NVDA", "status": "to do"}', encoding="utf-8")

    run_analista_agent.mark_request_done(request_file, {"ticker": "NVDA", "status": "to do"})

    content = request_file.read_text(encoding="utf-8")
    assert '"status": "done"' in content


def test_validate_generated_report_rejects_placeholders(tmp_path):
    """Test that unreplaced placeholders are rejected."""
    report_file = tmp_path / "informe-tecnico.md"
    report_file.write_text("Ingresos: {{PRECIO_ACTUAL}}", encoding="utf-8")

    valid, message = run_analista_agent.validate_generated_report(report_file)

    assert valid is False
    assert "unreplaced placeholders" in message


def test_validate_generated_report_accepts_real_figures(tmp_path):
    """Test that a report with real figures passes validation."""
    report_file = tmp_path / "informe-final.md"
    report_file.write_text(
        """
        Precio actual: 222.34
        Market cap: $3,456,789,000
        Margen de seguridad: 18.5%
        Recomendación: compra
        """,
        encoding="utf-8",
    )

    valid, message = run_analista_agent.validate_generated_report(report_file, min_numeric_tokens=3)

    assert valid is True
    assert "validated informe-final.md" in message
