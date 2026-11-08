# Paired evaluation protocol

1. Freeze candidate bytes and record its hash before opening the holdout.
2. Run baseline and candidate with the same immutable inputs, preprocessing, inference parameters, evaluator revision, and seed schedule. For the bundled bootstrap utility, provide matching stable example IDs in the same order as both metric arrays; it rejects missing or duplicate IDs.
3. Preserve per-example pairing. Report the primary metric and each guardrail by split and relevant slice; include sample counts and failures.
4. Use the preregistered paired uncertainty method (for example, a paired bootstrap over example IDs). Report interval, confidence level, resampling count, seed, and analysis code revision.
5. For VLA policies, use offline metrics as a screen. Safety claims require controlled simulation and any physical validation must be bounded, supervised, and explicitly authorized.
6. If an input, evaluator, or candidate hash differs, stop and mark that comparison invalid rather than pooling it.

A point estimate or the synthetic example in this repository is not evidence of generalization.
