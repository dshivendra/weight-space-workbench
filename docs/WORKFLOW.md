# Experiment workflow

## Roles in the loop

The skill pack divides the work into focused responsibilities. `wsp-loop` owns sequencing and evidence transfer; the other skills do not silently skip predecessor artifacts.

| Stage | Required input | Output |
|---|---|---|
| Define | User goal and deployment context | `goal.json` with target metric, guardrails, and stop rule |
| Baseline | Pinned model and evaluator | Baseline report and artifact hashes |
| Inspect | Baseline failure slices and model structure | Evidence-backed edit hypothesis or `no-edit` conclusion |
| Edit | Approved hypothesis and immutable source | Candidate checkpoint and edit receipt |
| Evaluate | Baseline, candidate, fixed test protocol | Paired metrics, holdout metrics, safety metrics |
| Decide | Preregistered acceptance rules | `keep`, `revert`, or `new-hypothesis` decision |
| Release | Kept candidate and complete evidence | Versioned derivative, model card, and provenance |

## Decision protocol

1. Keep the model revision, task inputs, preprocessing, random seeds, and evaluator fixed for the paired comparison.
2. Compare at least the preregistered primary metric and every guardrail. A primary score gain cannot compensate for a failed safety or regression guardrail.
3. Use the held-out set only after the proposed edit is frozen. Do not tune against it.
4. If results are noisy, use paired bootstrap confidence intervals or repeated deterministic seeds. A gain smaller than observed variation is inconclusive.
5. Save rejected candidate receipts too. This prevents the same failed edit from being rediscovered as if it were new evidence.

## Direct edit versus fine-tuning

Direct weight-space programming edits selected parameter values without an optimizer. Fine-tuning updates weights through an optimization process over examples. Record which method was used; do not describe a fine-tuned checkpoint as a direct edit.

## Framework boundary

The included editor supports a single Safetensors file and one scalar delta. Octo's published checkpoint uses a JAX/Flax checkpoint format, so the Safetensors utility cannot edit it directly. Use a format-specific adapter and preserve the same receipt and evaluation requirements.
