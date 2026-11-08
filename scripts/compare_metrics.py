#!/usr/bin/env python3
"""Compare preregistered metrics; point estimates alone cannot justify a keep."""

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
    parser.add_argument("--min-absolute-improvement", type=float, default=0.0)
    parser.add_argument(
        "--uncertainty-status",
        choices=("passed", "failed", "unknown"),
        default="unknown",
        help="Result of the preregistered uncertainty analysis (computed externally)",
    )
    parser.add_argument(
        "--uncertainty-method",
        help="Name the paired uncertainty method when --uncertainty-status=passed",
    )
    parser.add_argument("--guard", action="append", type=parse_guard, default=[])
    args = parser.parse_args()

    if not math.isfinite(args.min_relative_improvement) or args.min_relative_improvement < 0:
        parser.error("min-relative-improvement must be finite and non-negative")
    if not math.isfinite(args.min_absolute_improvement) or args.min_absolute_improvement < 0:
        parser.error("min-absolute-improvement must be finite and non-negative")
    if args.uncertainty_status == "passed" and not args.uncertainty_method:
        parser.error("--uncertainty-method is required when uncertainty status is passed")
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
    relative_gain = gain / abs(before) if before != 0 else None
    relative_pass = relative_gain >= args.min_relative_improvement if relative_gain is not None else True
    primary_pass = (
        gain > 0
        and gain >= args.min_absolute_improvement
        and relative_pass
    )

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

    guardrails_pass = all(result["passed"] for result in guard_results)
    if not guardrails_pass or not primary_pass:
        decision = "revert"
    elif args.uncertainty_status == "passed":
        decision = "keep"
    else:
        decision = "inconclusive"
    report = {
        "decision": decision,
        "primary": {
            "metric": args.primary,
            "direction": args.direction,
            "baseline": before,
            "candidate": after,
            "absolute_gain": gain,
            "relative_gain": relative_gain,
            "minimum_absolute_improvement": args.min_absolute_improvement,
            "minimum_relative_improvement": args.min_relative_improvement,
            "passed": primary_pass,
        },
        "guardrails": guard_results,
        "uncertainty": {
            "status": args.uncertainty_status,
            "method": args.uncertainty_method,
            "source": "caller-provided; this utility does not estimate uncertainty",
        },
    }
    print(json.dumps(report, indent=2))
    return {"keep": 0, "revert": 1, "inconclusive": 2}[decision]


if __name__ == "__main__":
    raise SystemExit(main())
