#!/usr/bin/env python3
"""Prepare, validate, and compare manual Agent Skill behavior evaluations."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import sys

from validate_skill_pack import parse_frontmatter

CONDITIONS = ("with_skill", "baseline")
BASELINES = ("without_skill", "previous_version")


class EvalError(ValueError):
    """Raised when an evaluation fixture or result is incomplete or stale."""


def package_sha256(skill_dir: Path) -> str:
    """Hash every package file by relative path and content, deterministically."""
    digest = hashlib.sha256()
    files = sorted(
        path for path in skill_dir.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    if not files:
        raise EvalError(f"skill package has no files: {skill_dir}")
    for path in files:
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8")
        content_hash = hashlib.sha256(path.read_bytes()).digest()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(content_hash)
        digest.update(b"\n")
    return digest.hexdigest()


def load_suite(skill_dir: Path) -> tuple[dict[str, object], str, str]:
    skill_dir = skill_dir.expanduser().resolve()
    skill_file = skill_dir / "SKILL.md"
    eval_file = skill_dir / "evals" / "evals.json"
    if not skill_file.is_file():
        raise EvalError(f"SKILL.md not found in {skill_dir}")
    if not eval_file.is_file():
        raise EvalError(f"evals/evals.json not found in {skill_dir}")
    metadata, _ = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    suite = json.loads(eval_file.read_text(encoding="utf-8"))
    if not isinstance(suite, dict):
        raise EvalError("evals/evals.json root must be a JSON object")
    skill_name = metadata.get("name")
    if not isinstance(skill_name, str) or suite.get("skill_name") != skill_name:
        raise EvalError("SKILL.md name and eval suite skill_name must match")
    cases = suite.get("evals")
    if not isinstance(cases, list) or not cases:
        raise EvalError("eval suite must contain at least one case")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise EvalError("every eval case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, (str, int)) or not str(case_id).strip():
            raise EvalError("every eval case requires a non-empty string or integer id")
        if str(case_id) in seen:
            raise EvalError(f"duplicate eval case id: {case_id}")
        seen.add(str(case_id))
        for field in ("prompt", "expected_output"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise EvalError(f"eval case {case_id} requires non-empty `{field}`")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions or any(not isinstance(a, str) or not a.strip() for a in assertions):
            raise EvalError(f"eval case {case_id} requires non-empty assertion strings")
    version = metadata.get("metadata", {}).get("version", "unknown") if isinstance(metadata.get("metadata"), dict) else "unknown"
    return suite, str(skill_name), str(version)


def atomic_write(path: Path, content: str) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def prepare(skill_dir: Path, output: Path, baseline_kind: str, baseline_skill: Path | None) -> dict[str, object]:
    skill_dir = skill_dir.expanduser().resolve()
    _ensure_output_outside_skill(skill_dir, output)
    suite, name, version = load_suite(skill_dir)
    if baseline_kind == "previous_version" and baseline_skill is None:
        raise EvalError("--baseline-skill is required when --baseline previous_version")
    if baseline_kind == "without_skill" and baseline_skill is not None:
        raise EvalError("--baseline-skill applies only with --baseline previous_version")
    cases = suite["evals"]
    package_hash = package_sha256(skill_dir.resolve())
    baseline_package_hash = None
    baseline_version = None
    if baseline_skill is not None:
        baseline_skill = baseline_skill.expanduser().resolve()
        baseline_skill_file = baseline_skill / "SKILL.md"
        if not baseline_skill_file.is_file():
            raise EvalError(f"baseline skill has no SKILL.md: {baseline_skill}")
        baseline_metadata, _ = parse_frontmatter(baseline_skill_file.read_text(encoding="utf-8"))
        if baseline_metadata.get("name") != name:
            raise EvalError("baseline skill name must match the candidate skill")
        baseline_package_hash = package_sha256(baseline_skill)
        if baseline_package_hash == package_hash:
            raise EvalError("candidate and baseline skill packages are identical")
        metadata = baseline_metadata.get("metadata")
        baseline_version = metadata.get("version", "unknown") if isinstance(metadata, dict) else "unknown"
    runs: list[dict[str, object]] = []
    for condition in CONDITIONS:
        for case in cases:
            runs.append({
                "condition": condition,
                "case_id": str(case["id"]),
                "prompt": case["prompt"],
                "expected_output": case["expected_output"],
                "files": case.get("files", []),
                "output_ref": "",
                "duration_ms": None,
                "total_tokens": None,
                "assertion_results": [
                    {"text": assertion, "passed": None, "evidence": ""}
                    for assertion in case["assertions"]
                ],
            })
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "skill_name": name,
        "skill_version": version,
        "skill_sha256": package_hash,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_kind": baseline_kind,
        "baseline_skill_sha256": baseline_package_hash,
        "baseline_skill_version": baseline_version,
        "conditions": list(CONDITIONS),
        "grading_guidance": "Use expected_output and assertions only for grading, not as part of the execution prompt. Every pass or fail needs evidence from the saved output.",
        "runs": runs,
        "review_notes": "",
    }
    atomic_write(output, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return {"skill_name": name, "skill_version": version, "cases": len(cases), "runs": len(runs), "skill_sha256": package_hash, "output": str(output.resolve())}


def _finite_nonnegative(value: object, label: str) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise EvalError(f"{label} must be a finite non-negative number or null")
    return value


def build_report(skill_dir: Path, results_path: Path) -> dict[str, object]:
    suite, name, version = load_suite(skill_dir)
    results = json.loads(results_path.expanduser().read_text(encoding="utf-8"))
    if not isinstance(results, dict):
        raise EvalError("results root must be a JSON object")
    if results.get("schema_version") != "1.0":
        raise EvalError("results schema_version must be 1.0")
    if results.get("skill_name") != name:
        raise EvalError("results skill_name does not match the package")
    if results.get("skill_sha256") != package_sha256(skill_dir.resolve()):
        raise EvalError("skill package changed after preparation; prepare a fresh results file")
    if results.get("skill_version") != version:
        raise EvalError("results skill_version does not match the package")
    baseline_kind = results.get("baseline_kind")
    if baseline_kind not in BASELINES:
        raise EvalError(f"baseline_kind must be one of: {', '.join(BASELINES)}")
    if baseline_kind == "previous_version" and not results.get("baseline_skill_sha256"):
        raise EvalError("previous-version comparison requires baseline_skill_sha256")

    cases = suite["evals"]
    cases_by_id = {str(case["id"]): case for case in cases}
    raw_runs = results.get("runs")
    if not isinstance(raw_runs, list):
        raise EvalError("runs must be an array")
    required_keys = {(condition, case_id) for condition in CONDITIONS for case_id in cases_by_id}
    seen: set[tuple[str, str]] = set()
    by_condition: dict[str, list[dict[str, object]]] = {condition: [] for condition in CONDITIONS}
    for run in raw_runs:
        if not isinstance(run, dict):
            raise EvalError("every run must be an object")
        condition, case_id = run.get("condition"), str(run.get("case_id", ""))
        if condition not in CONDITIONS:
            raise EvalError(f"run condition must be one of: {', '.join(CONDITIONS)}")
        key = (condition, case_id)
        if key not in required_keys:
            raise EvalError(f"unexpected run: condition={condition!r}, case_id={case_id!r}")
        if key in seen:
            raise EvalError(f"duplicate run: condition={condition}, case_id={case_id}")
        seen.add(key)
        if not isinstance(run.get("output_ref"), str) or not run["output_ref"].strip():
            raise EvalError(f"{condition}/{case_id} requires output_ref")
        _finite_nonnegative(run.get("duration_ms"), f"{condition}/{case_id}.duration_ms")
        _finite_nonnegative(run.get("total_tokens"), f"{condition}/{case_id}.total_tokens")
        expected_assertions = cases_by_id[case_id]["assertions"]
        actual = run.get("assertion_results")
        if not isinstance(actual, list) or len(actual) != len(expected_assertions):
            raise EvalError(f"{condition}/{case_id} must grade every expected assertion")
        checked: list[dict[str, object]] = []
        for expected, item in zip(expected_assertions, actual):
            if not isinstance(item, dict) or item.get("text") != expected:
                raise EvalError(f"{condition}/{case_id} assertion text does not match the frozen eval")
            if not isinstance(item.get("passed"), bool):
                raise EvalError(f"{condition}/{case_id} assertion `{expected}` must have passed=true or false")
            if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
                raise EvalError(f"{condition}/{case_id} assertion `{expected}` requires evidence")
            checked.append(item)
        by_condition[condition].append({**run, "assertion_results": checked})
    missing = sorted(required_keys - seen)
    if missing:
        raise EvalError("missing runs: " + ", ".join(f"{c}/{i}" for c, i in missing))

    summary: dict[str, object] = {}
    for condition, runs in by_condition.items():
        assertions = [item for run in runs for item in run["assertion_results"]]
        case_passes = sum(all(item["passed"] for item in run["assertion_results"]) for run in runs)
        durations = [run["duration_ms"] for run in runs if run.get("duration_ms") is not None]
        tokens = [run["total_tokens"] for run in runs if run.get("total_tokens") is not None]
        summary[condition] = {
            "runs": len(runs),
            "assertions_passed": sum(bool(item["passed"]) for item in assertions),
            "assertions_total": len(assertions),
            "assertion_pass_rate": sum(bool(item["passed"]) for item in assertions) / len(assertions),
            "cases_passed": case_passes,
            "cases_total": len(runs),
            "case_pass_rate": case_passes / len(runs),
            "mean_duration_ms": sum(durations) / len(durations) if durations else None,
            "duration_samples": len(durations),
            "mean_total_tokens": sum(tokens) / len(tokens) if tokens else None,
            "token_samples": len(tokens),
        }
    candidate, baseline = summary["with_skill"], summary["baseline"]
    report = {
        "schema_version": "1.0",
        "skill_name": name,
        "skill_version": version,
        "skill_sha256": results["skill_sha256"],
        "baseline_kind": baseline_kind,
        "baseline_skill_sha256": results.get("baseline_skill_sha256"),
        "conditions": summary,
        "delta_with_skill_minus_baseline": {
            "assertion_pass_rate": candidate["assertion_pass_rate"] - baseline["assertion_pass_rate"],
            "case_pass_rate": candidate["case_pass_rate"] - baseline["case_pass_rate"],
            "mean_duration_ms": _difference(candidate["mean_duration_ms"], baseline["mean_duration_ms"]),
            "mean_total_tokens": _difference(candidate["mean_total_tokens"], baseline["mean_total_tokens"]),
        },
        "review_notes": results.get("review_notes", ""),
        "interpretation": "This report summarizes scored scenarios; it does not establish general skill quality without prompt coverage and human review.",
    }
    return report


def _difference(a: object, b: object) -> float | None:
    return a - b if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None


def _ensure_output_outside_skill(skill_dir: Path, output: Path) -> None:
    resolved = output.expanduser().resolve()
    if resolved == skill_dir or skill_dir in resolved.parents:
        raise EvalError("evaluation workspaces must be written outside the skill package")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare", help="Create a frozen grading workspace from a skill eval suite")
    prepare_parser.add_argument("skill_dir", type=Path)
    prepare_parser.add_argument("--output", required=True, type=Path)
    prepare_parser.add_argument("--baseline", choices=BASELINES, default="without_skill")
    prepare_parser.add_argument("--baseline-skill", type=Path, help="Previous skill snapshot; required for --baseline previous_version")
    report_parser = subparsers.add_parser("report", help="Validate grades and calculate with-skill versus baseline metrics")
    report_parser.add_argument("skill_dir", type=Path)
    report_parser.add_argument("--results", required=True, type=Path)
    report_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            summary = prepare(args.skill_dir, args.output, args.baseline, args.baseline_skill)
        else:
            _ensure_output_outside_skill(args.skill_dir.expanduser().resolve(), args.output)
            summary = build_report(args.skill_dir, args.results)
            atomic_write(args.output, json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
            summary = {"skill_name": summary["skill_name"], "report": str(args.output.resolve()), "delta": summary["delta_with_skill_minus_baseline"]}
    except (OSError, UnicodeError, json.JSONDecodeError, EvalError, ValueError) as error:
        print(f"skill evaluation error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
