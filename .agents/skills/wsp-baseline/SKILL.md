---
name: wsp-baseline
description: "Use before proposing or applying a neural-network weight edit. Pin the model, checkpoint, data, preprocessing, evaluator, seeds, and metrics, then record the reproducible baseline."
license: MIT
metadata:
  version: "0.3.0"
  category: machine-learning
---

# Establish the baseline

1. Resolve the model to an immutable commit or local artifact. Record SHA-256 hashes for checkpoint files and configuration.
2. Record framework/library versions, device, dtype, tokenizer/image preprocessing, action normalization, and inference settings.
3. Pin dataset revision, split, filtering, sample IDs, and seed. Keep a separate untouched holdout set.
4. Run the model-specific evaluator without changing weights. Save per-example outputs when privacy permits.
5. Report sample count, primary metric, guardrail metrics, runtime/memory, and variability across seeds or repeated runs.
6. Confirm that the baseline is valid before continuing. If loading or evaluation fails, classify it as an environment/evaluator failure rather than a model score.

## Baseline checklist

- Exact model ID/revision and checkpoint hash
- Evaluation code revision and environment
- Dataset IDs, revisions, split, preprocessing, and sample count
- Fixed random seeds and inference parameters
- Per-example outputs or a secure reference to them
- Primary and regression metrics with uncertainty

## Output

Write `baseline.json` using `assets/baseline-record.json`. If the full repository is checked out, also fill `evaluation.baseline_metrics` in `templates/run-record.json`. Include the hashes and exact evaluation configuration needed to reproduce the result. Do not edit, fine-tune, merge, quantize, or convert the baseline checkpoint in place.

## Supporting files

- Run `python3 scripts/hash_artifacts.py MODEL_PATH DATA_PATH EVALUATOR_PATH` to create a deterministic SHA-256 inventory. Save stdout as the baseline artifact manifest.
- Use `assets/baseline-record.json` to capture the baseline identity, environment, seeds, and metrics.
- Read `references/reproducibility.md` when recording preprocessing, runtime, seed, and repeated-run details.
- Review `evals/evals.json` for missing-evaluator and incomplete-baseline cases.
