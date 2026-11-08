# Stage handoff contract

| Stage | Required artifact | Stop when |
|---|---|---|
| Goal | `goal.json` or completed task fields | target or metric is ambiguous |
| Baseline | immutable model/data/evaluator IDs, hashes, outputs, metrics | model-specific evaluator or valid data is unavailable |
| Inspect | evidence-linked hypothesis or `no-edit` | tensor-to-failure link is speculative |
| Edit | candidate hash and receipt | source is stale, bounds fail, or output path exists |
| Evaluate | paired and frozen-holdout results | parity, integrity, or guardrail fails |
| Decide | `keep`, `revert`, or `inconclusive` plus reason | a `keep` cannot meet preregistered evidence bar |
| Release | derivative manifest and verified artifact | non-keep decision or unresolved license/provenance |

Pass artifact paths and hashes, not summaries alone. Every stop should preserve completed artifacts and record the blocker so the next run can resume without claiming the stopped stage succeeded.
