#!/usr/bin/env python3
"""Fail-closed capability negotiation for a WSP broker request.

This helper is a policy primitive, not a security boundary by itself. A broker
must call it (or the equivalent library function) before dispatching an
operation, and the agent must not have direct access to adapter artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """Raised when a capability descriptor or request is malformed."""


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"{label}: cannot read JSON object: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"{label}: expected a JSON object")
    return value


def _operation_set(descriptor: dict[str, Any], label: str, field: str) -> set[str]:
    values = descriptor.get(field)
    if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
        raise ContractError(f"{label}.{field}: expected a list of non-empty strings")
    if len(values) != len(set(values)):
        raise ContractError(f"{label}.{field}: duplicate entries are not allowed")
    return set(values)


def canonical_digest(value: dict[str, Any]) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    except (TypeError, ValueError) as error:
        raise ContractError(f"value cannot be canonically encoded: {error}") from error
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def negotiate(
    broker: dict[str, Any],
    adapter: dict[str, Any],
    artifact: dict[str, Any],
    policy: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    """Return an auditable decision; malformed inputs fail closed."""
    descriptors = (("broker", broker), ("adapter", adapter), ("artifact", artifact), ("policy", policy))
    for label, descriptor in descriptors:
        if not isinstance(descriptor, dict):
            raise ContractError(f"{label}: expected a JSON object")
        if descriptor.get("schema_version") != "1.0":
            raise ContractError(f"{label}.schema_version: expected '1.0'")
    if not isinstance(request, dict):
        raise ContractError("request: expected a JSON object")

    broker_ops = _operation_set(broker, "broker", "operations")
    adapter_ops = _operation_set(adapter, "adapter", "operations")
    artifact_ops = _operation_set(artifact, "artifact", "operations")
    policy_ops = _operation_set(policy, "policy", "allowed_operations")
    negotiated = sorted(broker_ops & adapter_ops & artifact_ops & policy_ops)

    operation = request.get("operation")
    artifact_format = request.get("artifact_format")
    if not isinstance(operation, str) or not operation:
        raise ContractError("request.operation: expected a non-empty string")
    if not isinstance(artifact_format, str) or not artifact_format:
        raise ContractError("request.artifact_format: expected a non-empty string")

    adapter_formats = adapter.get("artifact_formats")
    artifact_formats = artifact.get("artifact_formats")
    for values, label in ((adapter_formats, "adapter.artifact_formats"), (artifact_formats, "artifact.artifact_formats")):
        if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
            raise ContractError(f"{label}: expected a list of non-empty strings")
        if len(values) != len(set(values)):
            raise ContractError(f"{label}: duplicate entries are not allowed")

    allowed = operation in negotiated
    format_supported = artifact_format in adapter_formats and artifact_format in artifact_formats
    supported = allowed and format_supported
    if supported:
        reason = "supported_by_all_capability_sets"
    elif not format_supported:
        reason = "CAPABILITY_NOT_SUPPORTED:artifact_format"
    else:
        reason = "CAPABILITY_NOT_SUPPORTED:operation"

    descriptor_bundle = {
        "broker": broker,
        "adapter": adapter,
        "artifact": artifact,
        "policy": policy,
    }
    return {
        "supported": supported,
        "reason": reason,
        "requested_operation": operation,
        "requested_artifact_format": artifact_format,
        "negotiated_operations": negotiated,
        "descriptor_bundle_sha256": canonical_digest(descriptor_bundle),
        "request_sha256": canonical_digest(request),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("broker", "adapter", "artifact", "policy", "request"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()
    try:
        inputs = {
            name: _load_object(getattr(args, name), name)
            for name in ("broker", "adapter", "artifact", "policy", "request")
        }
        result = negotiate(**inputs)
    except ContractError as error:
        print(json.dumps({"supported": False, "reason": "INVALID_CONTRACT", "error": str(error)}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["supported"] else 3


if __name__ == "__main__":
    sys.exit(main())
