# Hypothesis evidence test

Keep three layers separate:

1. **Observation:** measured output, failure examples, tensor shape/dtype, activation, or attribution result, with an artifact reference.
2. **Interpretation:** why this evidence could connect the module to the target failure, and what alternative could explain it.
3. **Prediction:** the direction and minimum change expected in the primary metric, which guardrails could move, and what result would disprove the link.

A tensor name, large magnitude, correlation, or attention map alone does not establish causal semantics. If no intervention is justified, write `no-edit` and preserve the baseline. The metadata inspector intentionally does not print weights or assign meaning to tensor names.
