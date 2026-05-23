#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

import validate_pre_commit as vp


def test_missing_tests_creates_log_and_transcript(tmp_path, monkeypatch):
    repo_root = Path.cwd()
    # Ensure logs dir is clean
    logs_dir = repo_root / ".github" / "hooks" / "logs" / "pre_commit_validator"
    if logs_dir.exists():
        shutil.rmtree(logs_dir)

    # Patch get_staged_files to simulate a staged Python file without tests
    monkeypatch.setattr(vp, "get_staged_files", lambda: ["src/new_feature.py"])

    result = vp.validate_commit()

    # Expect ask decision and transcript_path present
    assert "hookSpecificOutput" in result
    assert "transcript_path" in result

    transcript = Path(result["transcript_path"])
    assert transcript.exists()

    content = json.loads(transcript.read_text())
    assert "missing_tests" in content
    missing = [p.replace("\\", "/") for p in content["missing_tests"]]
    assert "src/new_feature.py" in missing


def test_detects_existing_test_file(tmp_path, monkeypatch):
    repo_root = Path.cwd()
    tests_dir = repo_root / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Create a fake module and corresponding test
    module_path = repo_root / "src"
    module_path.mkdir(exist_ok=True)
    (module_path / "module_a.py").write_text("# dummy")
    (tests_dir / "test_module_a.py").write_text("# test for module_a")

    # Patch staged files
    monkeypatch.setattr(vp, "get_staged_files", lambda: [str(module_path / "module_a.py")])

    result = vp.validate_commit()

    # Should allow continue since test exists
    assert result.get("continue", False) is True
