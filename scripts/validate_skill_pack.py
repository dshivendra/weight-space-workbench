#!/usr/bin/env python3
"""Check basic Agent Skills folder and required-frontmatter conventions."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".agents" / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def frontmatter_fields(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("YAML frontmatter must end with ---") from error
    fields = {}
    for line in lines[1:end]:
        if line.startswith("name:") or line.startswith("description:"):
            key, value = line.split(":", 1)
            fields[key] = value.strip().strip("\"'")
    return fields


def main() -> int:
    if not ROOT.is_dir():
        print(f"missing skill root: {ROOT}", file=sys.stderr)
        return 1
    skill_dirs = sorted(path for path in ROOT.iterdir() if path.is_dir())
    errors = []
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        try:
            fields = frontmatter_fields(skill_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            errors.append(f"{skill_dir.name}: {error}")
            continue
        name = fields.get("name", "")
        description = fields.get("description", "")
        if not NAME_PATTERN.fullmatch(name):
            errors.append(f"{skill_dir.name}: invalid or missing skill name {name!r}")
        if name != skill_dir.name:
            errors.append(f"{skill_dir.name}: frontmatter name must match folder name")
        if not description:
            errors.append(f"{skill_dir.name}: missing description")
        elif len(description) > 1024:
            errors.append(f"{skill_dir.name}: description exceeds 1024 characters")
        line_count = len(skill_file.read_text(encoding="utf-8").splitlines())
        if line_count > 500:
            errors.append(f"{skill_dir.name}: SKILL.md exceeds 500 lines")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(skill_dirs)} skill folders (required fields and basic naming/length rules).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
