---
name: wsp-edit
description: "Use only after a valid baseline and falsifiable edit hypothesis exist. Apply a bounded, reversible direct weight edit to a copy and record integrity checks in a machine-readable receipt."
license: MIT
compatibility: The bundled script edits a single Safetensors checkpoint using PyTorch and Safetensors; other formats need a format-specific adapter.
metadata:
  version: "0.2.0"
  category: machine-learning
---

# Apply a controlled edit

1. Verify the immutable source checkpoint hash matches the run record.
2. Confirm the hypothesis names the target tensor and expected shape/value range.
3. Copy or stream the source into a new candidate path. Never overwrite the source.
4. Prefer one tensor or a narrowly justified set of coordinates. Record the exact pre-edit values.
5. Enforce absolute delta bounds and finite values. Reject NaN/Inf, shape mismatch, missing tensors, unexpected dtype, or stale expected values.
6. Save the candidate and an edit receipt with source/candidate hashes, tool version, tensor/index, old/new values, delta, and timestamp.
7. Reload the candidate through the model-specific loader and run a forward-pass smoke check before evaluation.

## Output

Use `scripts/apply_safetensors_delta.py` for its supported format. It changes one scalar and writes a candidate checkpoint plus an edit receipt. It does not decide which weight should change and does not imply that the edit is beneficial. Record candidate and receipt paths in the run record.

If the checkpoint format is not Safetensors, do not convert it silently. Use the framework's supported load/save API and preserve the same no-overwrite and provenance guarantees.
