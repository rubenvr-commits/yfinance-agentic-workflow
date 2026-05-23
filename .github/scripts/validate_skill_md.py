#!/usr/bin/env python3
"""Validate SKILL.md files for required frontmatter and constraints.

Checks:
- Frontmatter delimited by '---' con campos `name` y `description`.
- `SKILL.md` length < 500 lines.
- No emojis present.
"""
import sys
from pathlib import Path
import re

EMOJI_RE = re.compile("[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]", flags=re.UNICODE)

def parse_frontmatter(lines):
    if len(lines) < 3 or not lines[0].strip().startswith("---"):
        return {}
    fm = {}
    for line in lines[1:20]:
        if line.strip().startswith("---"):
            break
        if ":" in line:
            k,v = line.split(":",1)
            fm[k.strip()] = v.strip().strip('"')
    return fm

def validate(path: Path):
    txt = path.read_text(encoding="utf-8")
    lines = txt.splitlines()
    fm = parse_frontmatter(lines)
    errors = []
    if not fm.get("name"):
        errors.append("Missing frontmatter field: name")
    if not fm.get("description"):
        errors.append("Missing frontmatter field: description")
    if len(lines) > 500:
        errors.append(f"SKILL.md too long: {len(lines)} lines (>500)")
    if EMOJI_RE.search(txt):
        errors.append("SKILL.md contains emoji characters (not allowed)")
    return errors

def main(argv):
    repo_root = Path.cwd()
    # Find all SKILL.md files under .github/skills
    skills_dir = repo_root / ".github" / "skills"
    if not skills_dir.exists():
        print("No skills directory found.")
        return 0
    overall_ok = True
    for skill in skills_dir.rglob("SKILL.md"):
        errs = validate(skill)
        if errs:
            overall_ok = False
            print(f"{skill}: \n  " + "\n  ".join(errs))
        else:
            print(f"{skill}: OK")
    return 0 if overall_ok else 2

if __name__ == "__main__":
    sys.exit(main(sys.argv))
