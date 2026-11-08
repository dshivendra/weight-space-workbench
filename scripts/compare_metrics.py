#!/usr/bin/env python3
"""Apply a preregistered keep/revert rule to baseline and candidate metric JSON."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def read_metrics(path: Path) -> dict[str, float]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a JSON object of metric names to numeric values")
    values: dict[str, float] = {}
    for key, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{path}: metric {key!r} must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError(f"{path}: metric {key!r} must be finite")
        values[key] = numeric
    return values


def parse_guard(value: str) -> tuple[str, str, float]:
    for operator in ("<=", ">="):
        if operator in value:
            name, limit = value.split(operator, 1)
            name = name.strip()
            if not name:
                break
            try:
                limit_number = float(limit.strip())
            except ValueError as error:
                raise argparse.ArgumentTypeError("guard limit must be numeric") from error
            if not math.isfinite(limit_number):
                raise argparse.ArgumentTypeError("guard limit must be finite")
            return name, operator, limit_number
    raise argparse.ArgumentTypeError("guard format must be METRIC<=LIMIT or METRIC>=LIMIT")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--primary", required=True, help="Primary metric key")
    parser.add_argument("--direction", choices=("lower", "higher"), required=True)
    parser.add_argument("--min-relative-improvement", type=float, default=0.0)
    parser.add_argument("--guard", action="append", type=parse_guard, default=[])
    args = parser.parse_args()

    if not math.isfinite(args.min_relative_improvement) or args.min_relative_improvement < 0:
        parser.error("min-relative-improvement must be finite and non-negative")
    try:
        baseline = read_metrics(args.baseline)
        candidate = read_metrics(args.candidate)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))

    if args.primary not in baseline or args.primary not in candidate:
        parser.error(f"primary metric {args.primary!r} must exist in both files")

    before = baseline[args.primary]
    after = candidate[args.primary]
    gain = before - after if args.direction == "lower" else after - before
    denominator = abs(before)
    relative_gain = gain / denominator if denominator > 0 else (math.inf if gain > 0 else 0.0)
    primary_pass = gain > 0 and relative_gain >= args.min_relative_improvement

    guard_results = []
    for name, operator, limit in args.guard:
        if name not in candidate:
            parser.error(f"guard metric {name!r} is missing from candidate metrics")
        observed = candidate[name]
        passed = observed <= limit if operator == "<=" else observed >= limit
        guard_results.append({
            "metric": name,
            "operator": operator,
            "limit": limit,
            "candidate": observed,
            "passed": passed,
        })

    keep = primary_pass and all(result["passed"] for result in guard_results)
    report = {
        "decision": "keep" if keep else "revert_or_inconclusive",
        "primary": {
            "metric": args.primary,
            "direction": args.direction,
            "baseline": before,
            "candidate": after,
            "absolute_gain": gain,
            "relative_gain": relative_gain if math.isfinite(relative_gain) else None,
            "minimum_relative_improvement": args.min_relative_improvement,
            "passed": primary_pass,
        },
        "guardrails": guard_results,
        "uncertainty_note": "This utility does not estimate statistical uncertainty; evaluate that separately.",
    }
    print(json.dumps(report, indent=2))
    return 0 if keep else 1


if __name__ == "__main__":
    raise SystemExit(main())
