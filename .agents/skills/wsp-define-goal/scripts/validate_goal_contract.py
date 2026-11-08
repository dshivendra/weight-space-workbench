#!/usr/bin/env python3
"""Validate a goal contract before baseline measurement or weight editing."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="Goal contract JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid contract: {error}", file=sys.stderr)
        return 2
    errors: list[str] = []
    if not isinstance(data, dict):
        errors.append("root must be a JSON object")
    else:
        if not isinstance(data.get("model"), dict):
            errors.append("model must be an object")
        context = data.get("context")
        if not isinstance(context, dict):
            errors.append("context must be an object")
        elif context.get("mode") not in {"offline", "simulator", "hardware"}:
            errors.append("context.mode must be offline, simulator, or hardware")
        dataset = data.get("data")
        if not isinstance(dataset, dict):
            errors.append("data must be an object")
        elif not isinstance(dataset.get("split"), str) or not dataset["split"].strip():
            errors.append("data.split must be declared")
        if not isinstance(data.get("goal"), str) or not data["goal"].strip():
            errors.append("goal must describe the target behavior")
        primary = data.get("primary_metric")
        if not isinstance(primary, dict):
            errors.append("primary_metric must be an object")
        else:
            if not isinstance(primary.get("name"), str) or not primary["name"].strip():
                errors.append("primary_metric.name is required")
            if primary.get("direction") not in {"lower", "higher"}:
                errors.append("primary_metric.direction must be lower or higher")
            minimum = primary.get("minimum_improvement")
            if minimum is not None and (not isinstance(minimum, (int, float)) or isinstance(minimum, bool) or minimum < 0):
                errors.append("primary_metric.minimum_improvement must be non-negative or null")
            if not isinstance(primary.get("uncertainty_method"), str) or not primary["uncertainty_method"].strip():
                errors.append("primary_metric.uncertainty_method must be declared or explicitly set to unknown")
        if not isinstance(data.get("guardrails"), list):
            errors.append("guardrails must be an array")
        if not isinstance(data.get("stop_conditions"), list) or not data["stop_conditions"]:
            errors.append("stop_conditions must be a non-empty array")
        if not isinstance(data.get("rollback_condition"), str) or not data["rollback_condition"].strip():
            errors.append("rollback_condition must be explicit")
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "model_revision": data["model"].get("revision", "unknown") if isinstance(data.get("model"), dict) else "unknown"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
