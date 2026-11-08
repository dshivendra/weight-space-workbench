#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest for model/data/evaluator artifacts."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to hash")
    parser.add_argument("--output", type=Path, help="Optional JSON manifest path; default is stdout")
    args = parser.parse_args()
    records = []
    try:
        for supplied in args.paths:
            path = supplied.expanduser().resolve(strict=True)
            files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
            if not files:
                parser.error(f"no files found under {path}")
            for file_path in files:
                records.append({"path": str(file_path), "size_bytes": file_path.stat().st_size, "sha256": digest(file_path)})
    except (OSError, ValueError) as error:
        print(f"hashing failed: {error}", file=sys.stderr)
        return 2
    records.sort(key=lambda item: item["path"])
    output = json.dumps({"algorithm": "sha256", "files": records}, indent=2) + "\n"
    if args.output:
        try:
            args.output.expanduser().write_text(output, encoding="utf-8")
        except OSError as error:
            print(f"cannot write manifest: {error}", file=sys.stderr)
            return 2
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
