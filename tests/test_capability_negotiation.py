from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from negotiate_capabilities import ContractError, negotiate  # noqa: E402


class CapabilityNegotiationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.broker = {
            "schema_version": "1.0",
            "operations": ["read_bounded_slice", "scalar_delta_candidate", "commit_edit"],
        }
        self.adapter = {
            "schema_version": "1.0",
            "artifact_formats": ["safetensors-single-file"],
            "operations": ["read_bounded_slice", "scalar_delta_candidate"],
        }
        self.artifact = {
            "schema_version": "1.0",
            "artifact_formats": ["safetensors-single-file"],
            "operations": ["read_bounded_slice", "scalar_delta_candidate", "commit_edit"],
        }
        self.policy = {
            "schema_version": "1.0",
            "allowed_operations": ["read_bounded_slice", "scalar_delta_candidate", "commit_edit"],
        }
        self.request = {
            "operation": "scalar_delta_candidate",
            "artifact_format": "safetensors-single-file",
        }

    def test_negotiates_only_intersection(self) -> None:
        result = negotiate(self.broker, self.adapter, self.artifact, self.policy, self.request)
        self.assertTrue(result["supported"])
        self.assertEqual(result["negotiated_operations"], ["read_bounded_slice", "scalar_delta_candidate"])

    def test_rejects_commit_when_adapter_does_not_support_it(self) -> None:
        self.request["operation"] = "commit_edit"
        result = negotiate(self.broker, self.adapter, self.artifact, self.policy, self.request)
        self.assertFalse(result["supported"])
        self.assertEqual(result["reason"], "CAPABILITY_NOT_SUPPORTED:operation")

    def test_rejects_format_not_supported_by_adapter(self) -> None:
        self.request["artifact_format"] = "gguf"
        result = negotiate(self.broker, self.adapter, self.artifact, self.policy, self.request)
        self.assertFalse(result["supported"])
        self.assertEqual(result["reason"], "CAPABILITY_NOT_SUPPORTED:artifact_format")

    def test_rejects_malformed_capability_descriptor(self) -> None:
        self.adapter["operations"] = ["read_bounded_slice", "read_bounded_slice"]
        with self.assertRaisesRegex(ContractError, "duplicate"):
            negotiate(self.broker, self.adapter, self.artifact, self.policy, self.request)

    def test_rejects_unknown_schema_version(self) -> None:
        self.adapter["schema_version"] = "99.0"
        with self.assertRaisesRegex(ContractError, "schema_version"):
            negotiate(self.broker, self.adapter, self.artifact, self.policy, self.request)

    def test_bundled_adapter_does_not_claim_commit_or_execution(self) -> None:
        descriptor_path = ROOT / "adapters" / "safetensors-local-v1" / "capabilities.json"
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        self.assertNotIn("commit_edit", descriptor["operations"])
        self.assertFalse(descriptor["capabilities"]["execution_probe"])
        self.assertFalse(descriptor["capabilities"]["atomic_canonical_commit"])


if __name__ == "__main__":
    unittest.main()
