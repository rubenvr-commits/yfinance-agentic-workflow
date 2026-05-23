import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))


def test_validate_generated_json_accepts_valid_metrics(tmp_path, monkeypatch):
    # Build minimal valid metrics.json according to schema
    metrics = {
        "ticker": "TEST",
        "fecha": "2026-05-23",
        "precio_actual": 100.0,
        "precios_historicos": {"ultimos_6m": [{"date": "2026-01-01", "close": 90}], "ultimos_12m": [{"date": "2025-06-01", "close": 50}]},
        "valuations": {},
        "performance": {}
    }
    p = tmp_path / "metrics.json"
    p.write_text(json.dumps(metrics), encoding="utf-8")

    # Inject a fake jsonschema module so the script can be imported without the package
    class DummyValidationError(Exception):
        pass

    def dummy_validate(instance=None, schema=None):
        return True

    dummy = type("dummy", (), {"validate": staticmethod(dummy_validate), "ValidationError": DummyValidationError})
    monkeypatch.setitem(sys.modules, 'jsonschema', dummy)

    import importlib
    validate_mod = importlib.import_module('validate_generated_json')

    # Create a minimal temporary schema and point the finder at it
    simple_schema = {"type": "object"}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(simple_schema), encoding="utf-8")
    monkeypatch.setattr(validate_mod, 'find_schema_for', lambda target: schema_file)

    # Call validator main by setting sys.argv and expect return code 0
    monkeypatch.setattr(sys, 'argv', ["validate_generated_json.py", str(p)])
    rc = validate_mod.main()
    assert rc == 0
