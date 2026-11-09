# Changelog

## Unreleased

- Define the architecture-neutral broker and adapter contract, including explicit capability limits for the local Safetensors profile.
- Add fail-closed capability intersection and tests for unsupported operations, unsupported formats, malformed descriptors, and absent commit/execution capabilities.

## 0.2.0 — 2026-11-08

- Strengthen skill descriptions, provenance, output contracts, and keep/revert rules.
- Add specification-aware Agent Skills validation, utility tests, and CI across Python 3.10–3.12.
- Add an optional-dependency CI job that exercises real Safetensors edits, receipts, and no-overwrite behavior.
- Make metric comparison inconclusive until uncertainty evidence is supplied.
- Make the Safetensors edit write outputs through temporary files, verify the saved scalar, and refuse concurrent destination collisions.
- Rewrite the README with install/use guidance, support boundaries, quality badges, and a disclosed visitor counter.
- Add skill authoring guidance based on the official specification and public skill examples.

## 0.1.0 — 2026-11-08

- Add eight portable Agent Skills covering the weight-space experiment lifecycle.
- Add a bounded one-scalar Safetensors edit utility with provenance receipt.
- Add a preregistered metric comparison utility.
- Add a synthetic image/instruction-to-action example and install/structure helpers.
- Document evaluation, format, release, and safety boundaries.
