#!/usr/bin/env python3
"""Verify required release provenance fields and the checkpoint SHA-256."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

REQUIRED = ("base_model_id", "base_revision", "license", "dataset_revision", "evaluator_revision", "decision", "limitations", "checkpoint_path", "checkpoint_sha256")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Release manifest JSON")
    args = parser.parse_args()
    try:
        manifest_path = args.manifest.expanduser().resolve(strict=True)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid manifest: {error}", file=sys.stderr)
        return 2
    errors = []
    if not isinstance(manifest, dict):
        errors.append("manifest root must be an object")
    else:
        for field in REQUIRED:
            if field not in manifest or manifest[field] in (None, "", []):
                errors.append(f"missing required field: {field}")
        if manifest.get("decision") != "keep":
            errors.append("release requires decision=keep")
        relative = manifest.get("checkpoint_path")
        if isinstance(relative, str) and relative:
            artifact = (manifest_path.parent / relative).resolve()
            if manifest_path.parent not in artifact.parents:
                errors.append("checkpoint_path must remain inside the release directory")
            elif not artifact.is_file():
                errors.append(f"checkpoint does not exist: {relative}")
            else:
                actual = digest(artifact)
                expected = str(manifest.get("checkpoint_sha256", "")).removeprefix("sha256:")
                if actual != expected:
                    errors.append(f"checkpoint hash mismatch: expected {expected}, got {actual}")
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "checkpoint_sha256": "sha256:" + actual}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
