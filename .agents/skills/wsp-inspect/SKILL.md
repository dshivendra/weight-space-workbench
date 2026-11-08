---
name: wsp-inspect
description: "Use after baseline measurement and before selecting tensors. Inspect architecture, parameter metadata, and failure examples to form a cautious, testable weight-edit hypothesis—or conclude that no edit is justified."
license: MIT
metadata:
  version: "0.3.0"
  category: machine-learning
---

# Inspect weights and behavior

Use executable analysis for tensor statistics and model probes. Do not dump entire checkpoints into a language-model prompt.

## Procedure

1. Inspect model card, config, architecture code, preprocessing, and license; cite the exact revision.
2. Inspect tensor names, shapes, dtypes, parameter counts, finite-value status, and module mapping.
3. Examine correct and failing baseline examples, model outputs, and—when available—activations or attribution evidence.
4. Separate direct observations from interpretation. Raw weights alone rarely identify semantic behavior reliably.
5. Identify the narrowest module plausibly related to the failure and state an alternative explanation.
6. Write a falsifiable hypothesis: expected output change, specific tensor(s), bounded edit range, target metric, and a result that would disprove it.
7. If evidence cannot connect a tensor to the failure, return `no-edit` and recommend an appropriate data/optimizer-based method instead.

## Do not

- Infer learned semantics from a few large or arbitrary tensor values.
- Confuse parameter importance, activation magnitude, or correlation with causal effect.
- Select edits using held-out evaluation examples.
- Claim a model was understood merely because a dataset or behavior was guessed correctly.

## Output

Fill `assets/edit-hypothesis.md` with observations, interpretation, alternative explanations, tensor and coordinate scope, expected metric change, bounds, and a disconfirming result. If the full repository is checked out, you may mirror it to `templates/edit-hypothesis.md`. If the evidence does not justify a causal hypothesis, report `no-edit` and stop before the editor.

## Supporting files

- For a Safetensors checkpoint, run `python3 scripts/inspect_safetensors.py CHECKPOINT --max-tensors 200` to emit bounded tensor metadata without dumping values.
- Read `references/hypothesis-quality.md` before linking a parameter to behavior; it separates observation from causal interpretation.
- Review `evals/evals.json` for unsupported format and weak causal-evidence cases.
