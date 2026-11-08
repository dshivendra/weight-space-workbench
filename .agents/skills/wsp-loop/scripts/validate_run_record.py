#!/usr/bin/env python3
"""Check run-record structure and enforce extra evidence for a keep decision."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = {
    "model": ("repo_id", "revision", "artifact_sha256"),
    "task": ("goal", "primary_metric", "primary_metric_direction"),
    "evaluation": ("dataset_id", "dataset_revision", "split", "evaluator_revision", "sample_count"),
    "edit": ("method", "hypothesis"),
    "decision": ("outcome", "reason"),
}
PLACEHOLDERS = {"", "unknown", "replace-with-unique-id", "replace-with-iso-8601-time"}
SHA256 = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="Run record JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid run record: {error}", file=sys.stderr)
        return 2
    errors = []
    if not isinstance(data, dict):
        errors.append("root must be a JSON object")
    else:
        for section, fields in REQUIRED.items():
            value = data.get(section)
            if not isinstance(value, dict):
                errors.append(f"{section} must be an object")
                continue
            for field in fields:
                if field not in value:
                    errors.append(f"missing {section}.{field}")
        if isinstance(data.get("task"), dict) and data["task"].get("primary_metric_direction") not in {"lower", "higher"}:
            errors.append("task.primary_metric_direction must be lower or higher")
        if isinstance(data.get("evaluation"), dict):
            count = data["evaluation"].get("sample_count")
            if not isinstance(count, int) or count < 0:
                errors.append("evaluation.sample_count must be a non-negative integer")
        if isinstance(data.get("decision"), dict):
            decision = data["decision"].get("outcome")
            if decision not in {"keep", "revert", "inconclusive"}:
                errors.append("decision.outcome must be keep, revert, or inconclusive")
            if decision == "keep":
                evaluation = data.get("evaluation", {})
                model = data.get("model", {})
                edit = data.get("edit", {})
                method = evaluation.get("uncertainty_method") if isinstance(evaluation, dict) else None
                metrics = evaluation.get("candidate_metrics") if isinstance(evaluation, dict) else None
                baseline_metrics = evaluation.get("baseline_metrics") if isinstance(evaluation, dict) else None
                sample_count = evaluation.get("sample_count") if isinstance(evaluation, dict) else None
                model_hash = model.get("artifact_sha256") if isinstance(model, dict) else None
                candidate_hash = edit.get("candidate_sha256") if isinstance(edit, dict) else None
                receipt = edit.get("receipt_path") if isinstance(edit, dict) else None
                if not method or method in PLACEHOLDERS:
                    errors.append("keep requires evaluation.uncertainty_method")
                if not isinstance(metrics, dict) or not metrics:
                    errors.append("keep requires evaluation.candidate_metrics")
                if not isinstance(baseline_metrics, dict) or not baseline_metrics:
                    errors.append("keep requires evaluation.baseline_metrics")
                if not isinstance(sample_count, int) or sample_count < 1:
                    errors.append("keep requires evaluation.sample_count > 0")
                if not isinstance(model_hash, str) or not SHA256.fullmatch(model_hash):
                    errors.append("keep requires a full model SHA-256")
                if not isinstance(candidate_hash, str) or not SHA256.fullmatch(candidate_hash):
                    errors.append("keep requires a full candidate SHA-256")
                if not isinstance(receipt, str) or not receipt.strip():
                    errors.append("keep requires edit.receipt_path")
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "decision": data["decision"]["outcome"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
