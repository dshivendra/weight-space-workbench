from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_eval.py"
SOURCE_SKILL = ROOT / ".agents" / "skills" / "wsp-define-goal"


class SkillEvalHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skill = self.root / "wsp-define-goal"
        shutil.copytree(SOURCE_SKILL, self.skill)
        self.results = self.root / "grading.json"
        self.report = self.root / "report.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def prepare(self) -> dict:
        result = self.run_cli("prepare", str(self.skill), "--output", str(self.results))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(self.results.read_text(encoding="utf-8"))

    def test_prepare_creates_frozen_candidate_and_baseline_runs(self):
        payload = self.prepare()
        self.assertEqual(payload["conditions"], ["with_skill", "baseline"])
        self.assertEqual(len(payload["runs"]), 4)
        self.assertRegex(payload["skill_sha256"], re.compile(r"^[0-9a-f]{64}$"))
        self.assertTrue(all(run["prompt"] and run["expected_output"] and run["assertion_results"] for run in payload["runs"]))

    def test_report_compares_assertions_cases_and_effort(self):
        payload = self.prepare()
        for run in payload["runs"]:
            run["output_ref"] = f"outputs/{run['condition']}/{run['case_id']}.md"
            run["duration_ms"] = 100 if run["condition"] == "with_skill" else 80
            run["total_tokens"] = 500 if run["condition"] == "with_skill" else 400
            for index, assertion in enumerate(run["assertion_results"]):
                assertion["passed"] = run["condition"] == "with_skill" or index > 0
                assertion["evidence"] = "Observed expected behavior in saved output."
        self.results.write_text(json.dumps(payload), encoding="utf-8")

        result = self.run_cli("report", str(self.skill), "--results", str(self.results), "--output", str(self.report))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertGreater(report["delta_with_skill_minus_baseline"]["assertion_pass_rate"], 0)
        self.assertEqual(report["delta_with_skill_minus_baseline"]["mean_duration_ms"], 20)
        self.assertEqual(report["delta_with_skill_minus_baseline"]["mean_total_tokens"], 100)

    def test_report_rejects_missing_assertion_evidence(self):
        payload = self.prepare()
        for run in payload["runs"]:
            run["output_ref"] = "outputs/result.md"
            for assertion in run["assertion_results"]:
                assertion["passed"] = True
                assertion["evidence"] = ""
        self.results.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_cli("report", str(self.skill), "--results", str(self.results), "--output", str(self.report))
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires evidence", result.stderr)

    def test_report_rejects_skill_changed_after_prepare(self):
        self.prepare()
        skill_file = self.skill / "SKILL.md"
        skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n<!-- changed -->\n", encoding="utf-8")
        result = self.run_cli("report", str(self.skill), "--results", str(self.results), "--output", str(self.report))
        self.assertEqual(result.returncode, 2)
        self.assertIn("changed after preparation", result.stderr)

    def test_previous_version_baseline_requires_snapshot(self):
        result = self.run_cli("prepare", str(self.skill), "--output", str(self.results), "--baseline", "previous_version")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--baseline-skill is required", result.stderr)

    def test_previous_version_records_distinct_snapshot(self):
        previous = self.root / "previous"
        shutil.copytree(self.skill, previous)
        skill_file = previous / "SKILL.md"
        skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n<!-- older snapshot -->\n", encoding="utf-8")
        result = self.run_cli(
            "prepare", str(self.skill), "--output", str(self.results),
            "--baseline", "previous_version", "--baseline-skill", str(previous),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(self.results.read_text(encoding="utf-8"))
        self.assertNotEqual(payload["skill_sha256"], payload["baseline_skill_sha256"])
        self.assertEqual(payload["baseline_skill_version"], payload["skill_version"])

    def test_all_bundled_skill_eval_suites_prepare(self):
        skills_root = ROOT / ".agents" / "skills"
        skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
        self.assertGreaterEqual(len(skill_dirs), 1)
        for skill_dir in skill_dirs:
            output = self.root / f"{skill_dir.name}.json"
            result = self.run_cli("prepare", str(skill_dir), "--output", str(output))
            self.assertEqual(result.returncode, 0, f"{skill_dir.name}: {result.stderr}")
            self.assertGreater(len(json.loads(output.read_text(encoding="utf-8"))["runs"]), 0)


if __name__ == "__main__":
    unittest.main()
