---
name: wsp-decide
description: "Use after candidate evaluation to decide whether a neural-network weight edit is keepable, must be reverted, or is inconclusive under preregistered metrics, guardrails, uncertainty, and reproducibility rules."
license: MIT
metadata:
  version: "0.3.0"
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

## Output

Write exactly one outcome—`keep`, `revert`, or `inconclusive`—with the rationale, metric evidence, guardrail results, uncertainty method, and next action using `assets/decision-report.json`. If the full repository is checked out, also update the matching decision fields in its run record. A point-estimate-only comparison is never enough for `keep`.

## Supporting files

- Run `python3 scripts/compare_metrics.py --help` for the machine-readable threshold check. It accepts only caller-provided uncertainty status; it does not calculate confidence intervals.
- Read `references/decision-rules.md` when resolving ties, missing evidence, or guardrail failures.
- Review `evals/evals.json` for uncertainty, guardrail, and threshold-change cases.
