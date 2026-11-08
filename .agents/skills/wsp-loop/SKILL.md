---
name: wsp-loop
description: "Use when a user asks to inspect, directly edit, improve, or compare neural-network weights. Coordinate a reproducible goal-to-baseline-to-hypothesis-to-edit-to-evaluation loop and make a keep, revert, or inconclusive decision from preregistered evidence."
license: MIT
compatibility: Requires access to model artifacts and a model-specific evaluator for empirical claims. Included editing utility supports single-file Safetensors checkpoints only.
metadata:
  version: "0.3.0"
  category: machine-learning
---

# Weight-space experiment loop

Run the experiment as a sequence of evidence-bearing stages. Do not skip stages because a user asks for a quick edit; reduce scope instead. Before starting, confirm the model/checkpoint and evaluator are actually available. Never treat a synthetic example, planned command, or guessed tensor meaning as an experiment result.

## Sequence

1. Read `wsp-define-goal` and create a goal contract with a primary metric, regression guardrails, evaluation splits, and stop rule.
2. Read `wsp-baseline`. Pin the model revision, artifact hash, preprocessing, evaluator, data revision, and seed. Save baseline outputs before any edit.
3. Read `wsp-inspect`. Diagnose a concrete failure and write a falsifiable hypothesis connecting observed evidence to a specific tensor or module. If no defensible connection exists, report `no-edit`.
4. Read `wsp-edit`. Produce an immutable source copy, apply the smallest bounded change, and record the edit receipt.
5. Read `wsp-evaluate`. Run paired evaluation on the baseline examples and a frozen held-out set. Include all guardrail metrics and uncertainty.
6. Read `wsp-decide`. Apply the acceptance rules declared before the edit. Keep, revert, or mark inconclusive; do not change thresholds after seeing results.
7. Read `wsp-release` only for a kept candidate. Preserve provenance and publish as a derivative, never overwrite an upstream repository.

At every handoff, check that the predecessor artifact exists and that its hashes and identifiers match the run record. A missing artifact means stop at that stage and report the blocker; do not fabricate the next stage's input.

## Evidence handoff

Use bundled `assets/run-record.json` for the canonical run record and `assets/edit-hypothesis.md` for the hypothesis. Each stage must either produce its output or record why it could not. Keep raw outputs and checkpoint hashes alongside the run record.

## Stop conditions

- No baseline, no edit.
- No model-specific loading path, no claim that the checkpoint is valid.
- No held-out evaluation, no claim of generalization.
- Any failed guardrail means revert or stop.
- For physical systems, no deployment from offline metrics alone; require simulation and bounded human-supervised validation.
- If tools, dependencies, credentials, or artifacts are unavailable, report the blocker and preserve completed evidence. Never describe a proposed loop as a completed run.

## Completion output

Report the model and immutable revision, baseline/candidate hashes, edit receipt, paired and holdout metrics, uncertainty method, every guardrail result, final decision, and any stages not run. Run `scripts/validate_run_record.py` on the final JSON before calling the loop complete. Say `inconclusive` when required evidence is missing.

## Supporting files

- Run `python3 scripts/validate_run_record.py RUN_RECORD.json` from the skill directory before declaring the loop complete. A `keep` decision also requires candidate metrics and an uncertainty method.
- Use `assets/run-record.json` and `assets/edit-hypothesis.md` when the repository-level templates are not available.
- Read `references/stage-handoffs.md` when a required artifact is missing or a stage needs to stop safely.
- Review `evals/evals.json` for skip-baseline, weak-hypothesis, and holdout-leakage pressure cases.
