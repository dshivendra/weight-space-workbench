#!/usr/bin/env python3
"""Copy Agent Skills folders into a client-provided skill directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path,
                        help="Skill directory scanned by the target agent client")
    args = parser.parse_args()

    source_root = Path(__file__).resolve().parents[1] / ".agents" / "skills"
    destination = args.destination.expanduser().resolve()
    if not source_root.is_dir():
        parser.error(f"skill source directory not found: {source_root}")
    if destination == source_root or source_root in destination.parents:
        parser.error("destination cannot be inside this repository's source skill tree")

    destination.mkdir(parents=True, exist_ok=True)
    installed = []
    skipped = []
    for skill_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        target = destination / skill_dir.name
        if target.exists():
            skipped.append(skill_dir.name)
            continue
        shutil.copytree(skill_dir, target)
        installed.append(skill_dir.name)

    print(f"Installed: {', '.join(installed) if installed else '(none)'}")
    print(f"Skipped existing: {', '.join(skipped) if skipped else '(none)'}")
    print(f"Destination: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
