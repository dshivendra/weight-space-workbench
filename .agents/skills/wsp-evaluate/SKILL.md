---
name: wsp-evaluate
description: "Evaluate a candidate weight edit against its pinned baseline with paired examples, held-out data, task-relevant metrics, safety guardrails, and uncertainty reporting. Use after applying an edit and before keeping or publishing it."
metadata:
  version: "0.1.0"
  category: machine-learning
---

# Evaluate a candidate

1. Verify baseline and candidate hashes, loader success, preprocessing parity, and that the declared edit is the only weight difference.
2. Run baseline and candidate on the same fixed examples for paired comparison.
3. Run the frozen holdout set once after candidate freeze. Do not tune against it.
4. Compute the preregistered primary metric and every guardrail. Report per-slice results, sample counts, confidence/uncertainty, and failures.
5. For classifier/decision models, consider accuracy plus calibration-sensitive metrics (Brier score, log loss, calibration error) where probabilities are consumed.
6. For vision-language-action policies, include action error by dimension, task success in a simulator, constraint violations, and unsafe/invalid action counts. Offline loss is not a substitute for rollout evaluation.
7. If results are noisy, use a predeclared paired bootstrap or repeated seeds; do not add trials only after seeing a bad result.
8. Save exact commands, environment, outputs, and evaluator revision.

Stop if the model loader fails, data differs, candidate contains unexpected changes, or a safety guardrail fails. Mark incomplete evidence as incomplete, never as a pass.
