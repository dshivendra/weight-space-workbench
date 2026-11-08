from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillSupportScriptTests(unittest.TestCase):
    def run_script(self, relative: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / relative), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_hash_artifacts_emits_sha256_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "model.bin"
            target.write_bytes(b"tiny model")
            result = self.run_script(".agents/skills/wsp-baseline/scripts/hash_artifacts.py", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(result.stdout)
            self.assertEqual(manifest["files"][0]["sha256"], hashlib.sha256(b"tiny model").hexdigest())

    def test_run_record_validator_rejects_keep_without_uncertainty(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "record.json"
            record = {
                "model": {"repo_id": "x", "revision": "rev", "artifact_sha256": "sha256:x"},
                "task": {"goal": "g", "primary_metric": "accuracy", "primary_metric_direction": "higher"},
                "evaluation": {"dataset_id": "d", "dataset_revision": "rev", "split": "holdout", "evaluator_revision": "rev", "sample_count": 10, "candidate_metrics": {"accuracy": 0.8}},
                "edit": {"method": "direct-weight-edit", "hypothesis": "h"},
                "decision": {"outcome": "keep", "reason": "gain"},
            }
            path.write_text(json.dumps(record), encoding="utf-8")
            result = self.run_script(".agents/skills/wsp-loop/scripts/validate_run_record.py", str(path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("uncertainty_method", result.stdout)

    def test_release_validator_checks_artifact_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "candidate.safetensors"
            artifact.write_bytes(b"candidate checkpoint")
            manifest = {
                "base_model_id": "owner/model",
                "base_revision": "immutable-revision",
                "license": "MIT",
                "dataset_revision": "dataset-revision",
                "evaluator_revision": "evaluator-revision",
                "decision": "keep",
                "limitations": ["offline evaluation only"],
                "checkpoint_path": artifact.name,
                "checkpoint_sha256": "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest(),
            }
            path = root / "release-manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            result = self.run_script(".agents/skills/wsp-release/scripts/verify_release_bundle.py", str(path))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            artifact.write_bytes(b"tampered")
            result = self.run_script(".agents/skills/wsp-release/scripts/verify_release_bundle.py", str(path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("hash mismatch", result.stdout)

    def test_goal_contract_validator_accepts_complete_contract(self):
        template = json.loads((ROOT / ".agents/skills/wsp-define-goal/assets/goal-contract.json").read_text(encoding="utf-8"))
        template["goal"] = "Reduce invalid actions"
        template["primary_metric"].update({"name": "invalid_action_rate", "direction": "lower", "minimum_improvement": 0.01, "uncertainty_method": "paired bootstrap"})
        template["data"].update({"dataset_id": "owner/data", "revision": "rev", "split": "validation", "preprocessing": "fixed", "seed_policy": "fixed seeds"})
        template["stop_conditions"] = ["Any guardrail fails"]
        template["rollback_condition"] = "Invalid action rate worsens"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "goal.json"
            path.write_text(json.dumps(template), encoding="utf-8")
            result = self.run_script(".agents/skills/wsp-define-goal/scripts/validate_goal_contract.py", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_paired_bootstrap_reports_stable_interval_from_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "paired.json"
            path.write_text(json.dumps({"example_ids": ["a", "b", "c"], "baseline": [2, 3, 4], "candidate": [1, 2, 3]}), encoding="utf-8")
            result = self.run_script(
                ".agents/skills/wsp-evaluate/scripts/paired_bootstrap.py",
                str(path), "--direction", "lower", "--min-improvement", "0.5", "--resamples", "1000", "--seed", "42"
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["n"], 3)
        self.assertTrue(report["supports_minimum_improvement"])
        self.assertEqual(report["interval"], {"lower": 1.0, "upper": 1.0})


if __name__ == "__main__":
    unittest.main()
