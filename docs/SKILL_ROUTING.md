# Skill routing

This project uses eight focused skills. Route by what the user wants done and by which evidence already exists. Do not load all skills at the beginning of a task.

| Request | Entry skill | Routing decision |
|---|---|---|
| “Change/improve these weights,” “compare a tuned checkpoint,” or “run the complete loop” | `wsp-loop` | Coordinate stages in dependency order; load only the current stage skill and its needed references. |
| “Define success,” “what metric should we optimize?” | `wsp-define-goal` | Specify goal, metric, guardrails, data split, uncertainty, and stop conditions. |
| “Measure this model before any edit” or “reproduce the baseline” | `wsp-baseline` | Pin identity, evaluator, data, preprocessing, environment, seeds, metrics. |
| “Diagnose this measured failure” or “is this tensor a plausible target?” | `wsp-inspect` | Requires baseline outputs and failure examples; may conclude `no-edit`. |
| “Apply this bounded, justified change” | `wsp-edit` | Requires valid baseline and falsifiable hypothesis; never infer tensor meaning. |
| “Run paired and holdout evaluation” | `wsp-evaluate` | Requires unchanged evaluation protocol and valid candidate. |
| “Should we keep this?” | `wsp-decide` | Requires preregistered metrics, guardrails, uncertainty, and holdout evidence. |
| “Publish/package the derivative” | `wsp-release` | Requires user-requested release, `keep`, license/provenance review, and separate derivative identity. |
| “What is weight-space editing/baseline/fine-tuning?” | Direct answer | Explain the concept; do not create artifacts or report measurements. |

The full decision rules and examples live in the bundled [`wsp-loop` reference](../.agents/skills/wsp-loop/references/routing.md), so the router works after skills are installed without the repository documentation.

## Precedence and conflict handling

1. An explicit skill name chooses the scope, but does not override safety gates or evidence prerequisites.
2. A broad operational request enters through `wsp-loop`.
3. A focused task enters through its stage skill only when the required preceding evidence is present.
4. If a later-stage task is requested with missing evidence, report the earliest unsatisfied prerequisite and stop. Do not silently perform unrelated stages.
5. Conceptual questions do not route to a workflow merely because they contain a skill keyword.
6. The user's request to release remains separate from the experiment's `keep` decision.

## When to add a skill

Add one only for a distinct, reusable task with its own trigger, contract, output, and failure/stop rules. If it merely sequences existing stages, put it in the router or workflow. If its output is the same as an existing stage, improve that stage instead. A new skill change must include a route-table entry, README inventory entry, self-contained supporting files, and eval fixtures for positive match, near miss, missing prerequisites, and pressure to bypass a gate.

The project intentionally does not put gstack's host-specific `triggers` or `contract` fields in the portable Agent Skills frontmatter. Host adapters may be added later, but must be optional, explainable, and covered by explicit host-support documentation. Current routing is an instruction contract, not a deterministic keyword classifier or stop hook.
