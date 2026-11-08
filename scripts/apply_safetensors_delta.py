#!/usr/bin/env python3
"""Apply one bounded scalar delta to a Safetensors checkpoint copy."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_index(value: str) -> tuple[int, ...]:
    try:
        result = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError("index must be comma-separated integers, e.g. 0,3") from error
    if not result or any(part < 0 for part in result):
        raise argparse.ArgumentTypeError("index must contain one or more non-negative integers")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--tensor", required=True, help="Exact tensor key in the Safetensors file")
    parser.add_argument("--index", required=True, type=parse_index, help="Tensor coordinate, e.g. 0,3")
    parser.add_argument("--delta", required=True, type=float)
    parser.add_argument("--max-abs-delta", required=True, type=float)
    parser.add_argument("--expect-value", type=float, help="Optional stale-check for the source scalar")
    parser.add_argument("--expect-tolerance", type=float, default=0.0)
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()
    receipt_path = destination.with_suffix(destination.suffix + ".edit.json")

    if not source.is_file():
        parser.error(f"source file does not exist: {source}")
    if source == destination:
        parser.error("destination must differ from source; the source is never overwritten")
    if destination.exists() or receipt_path.exists():
        parser.error("destination or receipt already exists; choose a new path")
    if not math.isfinite(args.delta) or not math.isfinite(args.max_abs_delta):
        parser.error("delta and max-abs-delta must be finite")
    if args.max_abs_delta < 0 or abs(args.delta) > args.max_abs_delta:
        parser.error("delta exceeds the declared absolute bound")
    if args.expect_tolerance < 0 or not math.isfinite(args.expect_tolerance):
        parser.error("expect-tolerance must be finite and non-negative")
    if args.expect_value is not None and not math.isfinite(args.expect_value):
        parser.error("expect-value must be finite")

    try:
        import torch
        from safetensors import safe_open
        from safetensors.torch import load_file, save_file
    except ImportError as error:
        parser.error(f"install optional dependencies with `python -m pip install torch safetensors`: {error}")

    try:
        source_hash = sha256(source)
        with safe_open(str(source), framework="pt", device="cpu") as handle:
            metadata = handle.metadata()
        tensors = load_file(str(source), device="cpu")
        if sha256(source) != source_hash:
            parser.error("source checkpoint changed while it was being read")
    except Exception as error:
        parser.error(f"could not read Safetensors source: {error}")
    if args.tensor not in tensors:
        parser.error(f"tensor key not found: {args.tensor}")

    tensor = tensors[args.tensor]
    if not tensor.is_floating_point():
        parser.error(f"target tensor is not floating point: {tensor.dtype}")
    if len(args.index) != tensor.ndim:
        parser.error(f"index rank {len(args.index)} does not match tensor rank {tensor.ndim}")
    if any(index >= size for index, size in zip(args.index, tensor.shape)):
        parser.error(f"index {args.index} is outside tensor shape {tuple(tensor.shape)}")

    coordinate = args.index
    old_value = float(tensor[coordinate].item())
    if not math.isfinite(old_value):
        parser.error("source scalar is non-finite")
    if args.expect_value is not None and abs(old_value - args.expect_value) > args.expect_tolerance:
        parser.error(
            f"stale source value: expected {args.expect_value}, got {old_value} "
            f"(tolerance {args.expect_tolerance})"
        )

    new_value = old_value + args.delta
    if not math.isfinite(new_value):
        parser.error("resulting scalar would be non-finite")
    tensors[args.tensor][coordinate] = new_value

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        parser.error(f"could not create destination directory: {error}")
    temporary_paths: list[Path] = []
    reserved_paths: list[Path] = []
    try:
        def temporary_path(suffix: str) -> Path:
            descriptor, name = tempfile.mkstemp(
                prefix=f".{destination.name}.", suffix=suffix, dir=destination.parent
            )
            os.close(descriptor)
            path = Path(name)
            temporary_paths.append(path)
            return path

        candidate_temp = temporary_path(".safetensors.tmp")
        receipt_temp = temporary_path(".edit.json.tmp")
        save_file(tensors, str(candidate_temp), metadata=metadata)
        with safe_open(str(candidate_temp), framework="pt", device="cpu") as handle:
            saved_value = float(handle.get_tensor(args.tensor)[coordinate].item())
        expected_value = float(tensors[args.tensor][coordinate].item())
        if saved_value != expected_value:
            raise OSError("saved checkpoint did not preserve the edited scalar")

        for output_path in (destination, receipt_path):
            descriptor = os.open(output_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            reserved_paths.append(output_path)
    except FileExistsError:
        for path in temporary_paths:
            path.unlink(missing_ok=True)
        for path in reserved_paths:
            path.unlink(missing_ok=True)
        parser.error("destination or receipt already exists; choose a new path")
    except Exception as error:
        for path in temporary_paths:
            path.unlink(missing_ok=True)
        for path in reserved_paths:
            path.unlink(missing_ok=True)
        parser.error(f"could not prepare checkpoint output: {error}")

    candidate_hash = sha256(candidate_temp)
    receipt = {
        "schema_version": "1.0",
        "method": "direct_scalar_delta",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source),
        "source_sha256": source_hash,
        "candidate_path": str(destination),
        "candidate_sha256": candidate_hash,
        "tensor": args.tensor,
        "index": list(coordinate),
        "before": old_value,
        "delta": args.delta,
        "after": expected_value,
        "max_abs_delta": args.max_abs_delta,
        "tensor_shape": list(tensor.shape),
        "dtype": str(tensor.dtype),
        "note": "This receipt records a parameter edit; it does not establish model improvement.",
    }
    try:
        receipt_temp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(candidate_temp, destination)
        os.replace(receipt_temp, receipt_path)
    except Exception as error:
        for path in temporary_paths:
            path.unlink(missing_ok=True)
        for path in reserved_paths:
            path.unlink(missing_ok=True)
        parser.error(f"could not write candidate and edit receipt: {error}")
    for path in temporary_paths:
        path.unlink(missing_ok=True)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
