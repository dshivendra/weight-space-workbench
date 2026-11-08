---
name: wsp-evaluate
description: "Use after a candidate weight edit and before deciding or publishing. Compare it with the pinned baseline on paired examples and frozen holdout data, including task metrics, safety guardrails, and uncertainty."
license: MIT
metadata:
  version: "0.3.0"
  category: machine-learning
---

# Evaluate a candidate

1. Verify baseline and candidate hashes, loader success, preprocessing parity, and that the declared edit is the only weight difference.
2. Run baseline and candidate on the same fixed examples for paired comparison.
3. After freezing the candidate, run both baseline and candidate on the same untouched holdout with identical settings. Do not tune against those results.
4. Compute the preregistered primary metric and every guardrail. Report per-slice results, sample counts, confidence/uncertainty, and failures.
5. For classifier/decision models, consider accuracy plus calibration-sensitive metrics (Brier score, log loss, calibration error) where probabilities are consumed.
6. For vision-language-action policies, include action error by dimension, task success in a simulator, constraint violations, and unsafe/invalid action counts. Offline loss is not a substitute for rollout evaluation.
7. If results are noisy, use the bundled `scripts/paired_bootstrap.py` on paired per-example metric values or use the preregistered repeated-seed method; do not add trials only after seeing a bad result. Keep rows aligned by stable example IDs and check the required sample count before interpreting the interval.
8. Save exact commands, environment, outputs, and evaluator revision.

Stop if the model loader fails, data differs, candidate contains unexpected changes, or a safety guardrail fails. Mark incomplete evidence as incomplete, never as a pass.

## Output

Save the exact commands, metric values, sample counts, uncertainty result, data split, environment, and evaluator revision in an evaluation record following `assets/evaluation-record.json`. If the full repository is checked out, also update the matching run-record fields. Keep paired and holdout results distinguishable; do not combine them into one score.

## Supporting files

- Read `references/evaluation-protocol.md` when defining paired examples, holdout freeze, uncertainty reporting, and policy safety measures.
- Use `assets/evaluation-record.json` as the standalone results structure.
- Run `python3 scripts/paired_bootstrap.py --help` for the uncertainty utility. It assumes paired inputs were aligned correctly and does not correct for multiple comparisons.
- Example: `python3 scripts/paired_bootstrap.py assets/paired-metric-example.json --direction lower --min-improvement 0.01 --seed 42`.
- Review `evals/evals.json` for leakage, missing guardrail, and inconclusive-evidence cases.
