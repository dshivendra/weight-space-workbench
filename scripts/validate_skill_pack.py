#!/usr/bin/env python3
"""Validate the repository's Agent Skills against the published format rules."""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

from strictyaml import YAMLError, load

ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
RECOMMENDED_MAX_LINES = 500


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Return the YAML metadata and Markdown body, rejecting malformed headers."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must begin with YAML frontmatter (`---`)")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("YAML frontmatter must end with a closing `---`") from error
    if end == 1:
        raise ValueError("YAML frontmatter cannot be empty")
    try:
        metadata = load("\n".join(lines[1:end])).data
    except YAMLError as error:
        raise ValueError(f"invalid YAML frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return metadata, "\n".join(lines[end + 1 :]).strip()


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_dir}: missing SKILL.md"]
    try:
        text = skill_file.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
    except (OSError, UnicodeError, ValueError) as error:
        return [f"{skill_file}: {error}"]

    unexpected = set(metadata) - ALLOWED_FIELDS
    if unexpected:
        errors.append(f"{skill_file}: unsupported frontmatter fields: {', '.join(sorted(unexpected))}")

    name = metadata.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{skill_file}: `name` must be a non-empty string")
    else:
        normalized = unicodedata.normalize("NFKC", name.strip())
        if len(normalized) > MAX_NAME_LENGTH:
            errors.append(f"{skill_file}: `name` exceeds {MAX_NAME_LENGTH} characters")
        if normalized != normalized.lower():
            errors.append(f"{skill_file}: `name` must be lowercase")
        if normalized.startswith("-") or normalized.endswith("-") or "--" in normalized:
            errors.append(f"{skill_file}: `name` cannot start/end with `-` or contain `--`")
        if not all(char.isalnum() or char == "-" for char in normalized):
            errors.append(f"{skill_file}: `name` may contain only lowercase letters, digits, and hyphens")
        if normalized != unicodedata.normalize("NFKC", skill_dir.name):
            errors.append(f"{skill_file}: `name` must match its directory (`{skill_dir.name}`)")

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_file}: `description` must be a non-empty string")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"{skill_file}: `description` exceeds {MAX_DESCRIPTION_LENGTH} characters")

    compatibility = metadata.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            errors.append(f"{skill_file}: `compatibility` must be a string")
        elif len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            errors.append(f"{skill_file}: `compatibility` exceeds {MAX_COMPATIBILITY_LENGTH} characters")

    license_name = metadata.get("license")
    if license_name is not None and (not isinstance(license_name, str) or not license_name.strip()):
        errors.append(f"{skill_file}: `license` must be a non-empty string when provided")

    allowed_tools = metadata.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append(f"{skill_file}: `allowed-tools` must be a space-separated string")

    skill_metadata = metadata.get("metadata")
    if skill_metadata is not None:
        if not isinstance(skill_metadata, dict):
            errors.append(f"{skill_file}: `metadata` must be a key-value mapping")
        elif any(not isinstance(key, str) or not isinstance(value, str) for key, value in skill_metadata.items()):
            errors.append(f"{skill_file}: values in `metadata` must be strings")

    if not body:
        errors.append(f"{skill_file}: instructions body cannot be empty")
    line_count = len(text.splitlines())
    if line_count > RECOMMENDED_MAX_LINES:
        errors.append(f"{skill_file}: {line_count} lines exceeds the {RECOMMENDED_MAX_LINES}-line project limit")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / ".agents" / "skills",
        help="Directory containing one folder per skill",
    )
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"missing skill root: {root}", file=sys.stderr)
        return 1

    skill_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if not skill_dirs:
        print(f"no skill folders found in {root}", file=sys.stderr)
        return 1

    errors = [error for skill_dir in skill_dirs for error in validate_skill(skill_dir)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(skill_dirs)} Agent Skills under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
