#!/usr/bin/env python3
"""Validate generated JSON files against repository schemas.

Usage:
  python validate_generated_json.py path/to/metrics.json
"""
import sys
import json
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except Exception:
    print("jsonschema not installed. Install with: pip install jsonschema")
    sys.exit(2)

def find_schema_for(path: Path):
    txt = str(path).lower()
    repo_root = Path(__file__).resolve().parent.parent
    schemas_dir = repo_root / ".github" / "schemas"
    if "metrics.json" in txt:
        return schemas_dir / "metrics.schema.json"
    if "web-search.json" in txt or "web-search" in txt:
        return schemas_dir / "web-search.schema.json"
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_generated_json.py path/to/file.json")
        return 2

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"File not found: {target}")
        return 2

    schema_path = find_schema_for(target)
    if not schema_path or not schema_path.exists():
        print(f"No schema found for {target}; expected under .github/schemas")
        return 2

    data = json.loads(target.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(instance=data, schema=schema)
        print(f"OK: {target} validates against {schema_path}")
        return 0
    except ValidationError as e:
        print(f"Validation error for {target}: {e.message}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
