#!/usr/bin/env python3
"""Estimate a paired percentile-bootstrap interval for a scalar metric difference."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path


def percentile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paired", type=Path, help="JSON with equal-length baseline and candidate numeric arrays")
    parser.add_argument("--direction", choices=("lower", "higher"), required=True)
    parser.add_argument("--min-improvement", type=float, default=0.0, help="Minimum gain required for interval-based support")
    parser.add_argument("--confidence", type=float, default=0.95, help="Two-sided confidence level (default: 0.95)")
    parser.add_argument("--resamples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    invalid_parameters = (
        not math.isfinite(args.min_improvement)
        or args.min_improvement < 0
        or not math.isfinite(args.confidence)
        or not 0 < args.confidence < 1
        or args.resamples < 1000
    )
    if invalid_parameters:
        parser.error("require min-improvement >= 0, confidence in (0,1), and at least 1000 resamples")
    try:
        payload = json.loads(args.paired.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid paired data: {error}", file=sys.stderr)
        return 2
    ids = payload.get("example_ids") if isinstance(payload, dict) else None
    baseline = payload.get("baseline") if isinstance(payload, dict) else None
    candidate = payload.get("candidate") if isinstance(payload, dict) else None
    if (
        not isinstance(ids, list)
        or not isinstance(baseline, list)
        or not isinstance(candidate, list)
        or len(ids) != len(baseline)
        or len(ids) != len(candidate)
        or len(ids) < 2
        or any(not isinstance(item, (str, int)) or not str(item) for item in ids)
        or len({str(item) for item in ids}) != len(ids)
    ):
        print("paired data must contain unique example_ids and equal-length baseline/candidate arrays with at least two rows", file=sys.stderr)
        return 2
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) for value in baseline + candidate):
        print("all paired metric values must be finite numbers", file=sys.stderr)
        return 2
    sign = 1.0 if args.direction == "higher" else -1.0
    differences = [sign * (float(new) - float(old)) for old, new in zip(baseline, candidate)]
    rng = random.Random(args.seed)
    n = len(differences)
    bootstrap_means = sorted(sum(differences[rng.randrange(n)] for _ in range(n)) / n for _ in range(args.resamples))
    alpha = (1.0 - args.confidence) / 2.0
    lower = percentile(bootstrap_means, alpha)
    upper = percentile(bootstrap_means, 1.0 - alpha)
    mean_gain = sum(differences) / n
    report = {
        "method": "paired-percentile-bootstrap",
        "n": n,
        "confidence": args.confidence,
        "resamples": args.resamples,
        "seed": args.seed,
        "example_ids_sha256": hashlib.sha256(json.dumps(ids, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest(),
        "direction": args.direction,
        "minimum_improvement": args.min_improvement,
        "mean_improvement": mean_gain,
        "interval": {"lower": lower, "upper": upper},
        "supports_minimum_improvement": lower > args.min_improvement,
        "interpretation": "The interval is computed from caller-provided paired per-example metric values; validate pairing and protocol before interpreting it.",
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
