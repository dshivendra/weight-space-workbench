# Route to the smallest correct skill

Use the user's intent and the evidence already available to choose the entry point. Skill selection never waives a stage prerequisite. If a request names a skill explicitly, honor that scope and stop at its first missing prerequisite; do not silently run the rest of the loop.

| User intent | Entry skill | Continue when | Stop when |
|---|---|---|---|
| Change, improve, tune, fine-tune, compare, or release model weights across multiple stages; request is broad or asks for the complete loop | `wsp-loop` | Execute only the stages whose inputs are present, in dependency order | Model/evaluator/data access or required evidence is missing; record the blocker and next prerequisite |
| Define success criteria or turn a vague behavior request into an experiment | `wsp-define-goal` | Goal, metric, guardrails, data split, and stop rule are explicit | A decision materially affecting the contract is unknown |
| Establish or reproduce pre-edit model performance | `wsp-baseline` | Model, data, preprocessing, evaluator, and immutable revisions are available | Loader/evaluator fails or baseline identity cannot be pinned |
| Diagnose a measured failure and determine whether a parameter hypothesis is defensible | `wsp-inspect` | Baseline outputs and failure examples exist | Evidence cannot connect the failure to a candidate module/tensor; return `no-edit` |
| Apply a bounded direct weight edit | `wsp-edit` | Valid baseline and falsifiable, approved hypothesis exist | Source hash, tensor mapping, bounds, or output location is missing/invalid |
| Measure a candidate using paired examples and a frozen holdout | `wsp-evaluate` | Baseline and candidate load under identical evaluation conditions | Protocol parity, holdout isolation, or guardrail measurement fails |
| Decide keep/revert/inconclusive from preregistered results | `wsp-decide` | Primary result, guardrails, uncertainty and holdout evidence are recorded | Any required result is missing; return `inconclusive` |
| Package or publish a derivative | `wsp-release` | User requests release and a documented `keep` decision plus provenance/license review exist | Decision, rights, integrity checks, or separate derivative identity are missing |
| Explain weight-space concepts without modifying or evaluating a checkpoint | No workflow skill required; answer directly | User asks to begin a concrete experiment | Do not create a run or imply work was executed |

## Selection rules

1. **Explicit stage request wins for scope, not for safety.** If the user says “run `wsp-edit`” but there is no baseline, do not edit; report the missing prerequisite.
2. **Broad change requests enter through `wsp-loop`.** Do not load every stage skill at once. Load the current stage and its directly linked references, then follow the handoff table.
3. **Route by current task, not by vocabulary alone.** “What is a baseline?” is an explanation request. “Measure this model before editing” is a baseline task.
4. **Choose the earliest unsatisfied prerequisite.** If a request asks to compare but no baseline exists, route to `wsp-baseline`; do not jump to `wsp-decide`.
5. **Keep the release path opt-in.** A `keep` result does not itself authorize publication. The user must ask for release.
6. **Do not invoke skills for excluded formats as if support existed.** Identify the format adapter and model-specific evaluator gap first; see `docs/SUPPORTED_FORMATS.md` when the full repository is available.

## Adding or changing a skill route

Add a route only when the task is repeatable, has a distinct activation condition, owns a distinct output or decision, and cannot be expressed as a short step in an existing skill. Before adding a skill:

- state its user intent in one sentence and name both positive examples and near-miss prompts;
- decide whether it is a new entry point or a stage called by `wsp-loop`;
- add it to this table and to the README skill inventory in the same change;
- define its required inputs, output artifact, stop conditions, and predecessor/successor;
- add eval scenarios for activation, non-activation, missing input, and pressure to bypass its gate;
- confirm the bundle is self-contained and points directly to each needed reference or script.

Do not add host-specific `triggers` or contract frontmatter to portable skill files. This repo's cross-host contract is `name` + `description` plus explicit routing guidance. Host-specific routing hooks may be added later as optional adapters with a portable fallback and an `--explain`/dry-run path.
