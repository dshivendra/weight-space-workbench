#!/usr/bin/env python3
"""Summarize Safetensors tensor metadata without printing parameter values."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path, help="Safetensors file to inspect")
    parser.add_argument("--max-tensors", type=int, default=200, help="Maximum tensor records to emit (default: 200)")
    args = parser.parse_args()
    if args.max_tensors < 1:
        parser.error("--max-tensors must be positive")
    try:
        from safetensors import safe_open
    except ImportError:
        print("missing dependency: install safetensors (see wsp-inspect/references/tooling.md)", file=sys.stderr)
        return 2
    try:
        path = args.checkpoint.expanduser().resolve(strict=True)
        if not path.is_file() or path.suffix != ".safetensors":
            parser.error("checkpoint must be an existing .safetensors file")
        with safe_open(str(path), framework="pt", device="cpu") as handle:
            keys = sorted(handle.keys())
            records = []
            for key in keys[:args.max_tensors]:
                tensor_slice = handle.get_slice(key)
                shape = list(tensor_slice.get_shape())
                records.append({"name": key, "shape": shape, "dtype": tensor_slice.get_dtype(), "numel": _product(shape)})
            header = handle.metadata() or {}
        print(json.dumps({"path": str(path), "tensor_count": len(keys), "emitted_count": len(records), "truncated": len(keys) > len(records), "metadata": header, "tensors": records}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"inspection failed: {error}", file=sys.stderr)
        return 2


def _product(shape: list[int]) -> int:
    result = 1
    for dim in shape:
        result *= dim
    return result


if __name__ == "__main__":
    raise SystemExit(main())
