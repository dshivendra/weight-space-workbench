from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_metrics.py"


class CompareMetricsTests(unittest.TestCase):
    def run_comparison(self, baseline: dict, candidate: dict, *extra: str):
        with tempfile.TemporaryDirectory() as directory:
            baseline_path = Path(directory) / "baseline.json"
            candidate_path = Path(directory) / "candidate.json"
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--baseline",
                    str(baseline_path),
                    "--candidate",
                    str(candidate_path),
                    "--primary",
                    "loss",
                    "--direction",
                    "lower",
                    *extra,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            return result

    def test_point_estimate_without_uncertainty_is_inconclusive(self):
        result = self.run_comparison({"loss": 1.0}, {"loss": 0.8})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["decision"], "inconclusive")

    def test_keep_requires_uncertainty_method_and_passing_guard(self):
        result = self.run_comparison(
            {"loss": 1.0},
            {"loss": 0.8, "invalid_actions": 0},
            "--uncertainty-status",
            "passed",
            "--uncertainty-method",
            "paired-bootstrap-95-percent-CI",
            "--guard",
            "invalid_actions<=0",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["decision"], "keep")

    def test_failed_guard_reverts_even_when_primary_improves(self):
        result = self.run_comparison(
            {"loss": 1.0},
            {"loss": 0.8, "invalid_actions": 1},
            "--uncertainty-status",
            "passed",
            "--uncertainty-method",
            "paired-bootstrap-95-percent-CI",
            "--guard",
            "invalid_actions<=0",
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["decision"], "revert")

    def test_uncertainty_pass_requires_method(self):
        result = self.run_comparison(
            {"loss": 1.0}, {"loss": 0.8}, "--uncertainty-status", "passed"
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--uncertainty-method is required", result.stderr)

    def test_zero_baseline_uses_absolute_improvement(self):
        result = self.run_comparison(
            {"loss": 0.0},
            {"loss": -0.2},
            "--min-absolute-improvement",
            "0.1",
            "--uncertainty-status",
            "passed",
            "--uncertainty-method",
            "paired-bootstrap",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIsNone(report["primary"]["relative_gain"])


if __name__ == "__main__":
    unittest.main()
