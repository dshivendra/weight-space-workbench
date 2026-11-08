---
name: wsp-decide
description: "Decide whether to keep, revert, or investigate a neural-network weight edit using acceptance rules declared before evaluation, including primary improvement, regression guardrails, uncertainty, and reproducibility."
metadata:
  version: "0.1.0"
  category: machine-learning
---

# Make the keep-or-revert decision

Apply the experiment contract exactly as written before evaluation.

## Keep only when

- The primary metric improves by at least the preregistered minimum on the primary comparison.
- Every guardrail passes; a gain in one metric cannot compensate for an unsafe or material regression in another.
- The improvement is larger than run-to-run uncertainty or its paired confidence interval supports the declared claim.
- The held-out result supports transfer beyond the examples used to diagnose the edit.
- The candidate, receipt, and evaluation evidence are complete and reproducible.

## Otherwise

- **Revert** when the target metric fails, a guardrail fails, or the edit causes unexpected behavior.
- **Inconclusive** when evidence is underpowered, evaluation is incomplete, or the gain is within noise. Do not call inconclusive a success.
- **New hypothesis** only after recording the prior attempt and its result. Do not silently tune thresholds or reuse the holdout as training data.

Write the decision, rationale, metrics, and next action into the run record.
