---
name: wsp-baseline
description: "Establish a reproducible baseline for a neural-network weight experiment by pinning the model, checkpoint, data, preprocessing, evaluator, seeds, and metrics before any weight changes. Use before proposing or applying an edit."
metadata:
  version: "0.1.0"
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

Output `baseline.json` or fill the `evaluation.baseline_metrics` section in `templates/run-record.json`. Do not edit, fine-tune, merge, quantize, or convert the baseline checkpoint in place.
