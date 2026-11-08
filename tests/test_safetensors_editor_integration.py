from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import torch
    from safetensors import safe_open
    from safetensors.torch import save_file
except ImportError:
    torch = None
    safe_open = None
    save_file = None

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apply_safetensors_delta.py"
INSPECT_SCRIPT = ROOT / ".agents" / "skills" / "wsp-inspect" / "scripts" / "inspect_safetensors.py"


@unittest.skipIf(torch is None, "install requirements-safetensors.txt for integration tests")
class SafetensorsEditorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source.safetensors"
        save_file(
            {"policy.weight": torch.tensor([1.25, -0.5], dtype=torch.float32)},
            str(self.source),
            metadata={"fixture": "small-policy"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_editor(self, destination: Path):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--source",
                str(self.source),
                "--destination",
                str(destination),
                "--tensor",
                "policy.weight",
                "--index",
                "0",
                "--delta",
                "0.25",
                "--max-abs-delta",
                "0.5",
                "--expect-value",
                "1.25",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_writes_one_bounded_scalar_and_receipt(self):
        destination = self.root / "candidate.safetensors"
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        result = self.run_editor(destination)

        self.assertEqual(result.returncode, 0, result.stderr)
        receipt_path = destination.with_suffix(".safetensors.edit.json")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), source_hash)
        self.assertEqual(receipt["source_sha256"], source_hash)
        self.assertEqual(receipt["candidate_sha256"], hashlib.sha256(destination.read_bytes()).hexdigest())
        self.assertEqual(receipt["before"], 1.25)
        self.assertEqual(receipt["after"], 1.5)
        with safe_open(str(destination), framework="pt", device="cpu") as checkpoint:
            self.assertEqual(checkpoint.metadata(), {"fixture": "small-policy"})
            values = checkpoint.get_tensor("policy.weight")
        self.assertEqual(values.tolist(), [1.5, -0.5])

    def test_existing_destination_is_never_overwritten(self):
        destination = self.root / "existing.safetensors"
        destination.write_bytes(b"keep this file")
        result = self.run_editor(destination)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(destination.read_bytes(), b"keep this file")
        self.assertFalse(destination.with_suffix(".safetensors.edit.json").exists())

    def test_inspector_emits_bounded_metadata_without_values(self):
        result = subprocess.run(
            [sys.executable, str(INSPECT_SCRIPT), str(self.source), "--max-tensors", "1"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["tensor_count"], 1)
        self.assertEqual(report["tensors"][0]["name"], "policy.weight")
        self.assertEqual(report["tensors"][0]["shape"], [2])
        self.assertNotIn("values", report["tensors"][0])


if __name__ == "__main__":
    unittest.main()
