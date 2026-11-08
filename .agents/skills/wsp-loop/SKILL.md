---
name: wsp-loop
description: "Orchestrate a complete, reproducible weight-space experiment: define a behavior target, pin model and data, measure a baseline, diagnose a failure, propose and apply a bounded weight edit, evaluate the candidate, and keep or revert it using preregistered criteria. Use when a user asks to inspect, edit, improve, or compare neural-network weights."
compatibility: Requires access to model artifacts and a model-specific evaluator for empirical claims. Included editing utility supports single-file Safetensors checkpoints only.
metadata:
  version: "0.1.0"
  category: machine-learning
---

# Weight-space experiment loop

Run the experiment as a sequence of evidence-bearing stages. Do not skip stages because a user asks for a quick edit; reduce scope instead.

## Sequence

1. Read `wsp-define-goal` and create a goal contract with a primary metric, regression guardrails, evaluation splits, and stop rule.
2. Read `wsp-baseline`. Pin the model revision, artifact hash, preprocessing, evaluator, data revision, and seed. Save baseline outputs before any edit.
3. Read `wsp-inspect`. Diagnose a concrete failure and write a falsifiable hypothesis connecting observed evidence to a specific tensor or module. If no defensible connection exists, report `no-edit`.
4. Read `wsp-edit`. Produce an immutable source copy, apply the smallest bounded change, and record the edit receipt.
5. Read `wsp-evaluate`. Run paired evaluation on the baseline examples and a frozen held-out set. Include all guardrail metrics and uncertainty.
6. Read `wsp-decide`. Apply the acceptance rules declared before the edit. Keep, revert, or mark inconclusive; do not change thresholds after seeing results.
7. Read `wsp-release` only for a kept candidate. Preserve provenance and publish as a derivative, never overwrite an upstream repository.

## Evidence handoff

Use `templates/run-record.json` for the canonical run record and `templates/edit-hypothesis.md` for the hypothesis. Each stage must either produce its output or record why it could not. Keep raw outputs and checkpoint hashes alongside the run record.

## Stop conditions

- No baseline, no edit.
- No model-specific loading path, no claim that the checkpoint is valid.
- No held-out evaluation, no claim of generalization.
- Any failed guardrail means revert or stop.
- For physical systems, no deployment from offline metrics alone; require simulation and bounded human-supervised validation.
- If tools, dependencies, credentials, or artifacts are unavailable, report the blocker and preserve completed evidence. Never describe a proposed loop as a completed run.
