# Skill system design review

This review records low-level implementation patterns inspected in Stageshow, Superpowers, gstack, and Matt Pocock's `grill-me`/`grilling`, and the decisions for this repository. It is a design adaptation, not a claim that this project implements those systems or copies their content.

## What the references actually implement

| System | Concrete mechanism | Adaptation here | Not adopted as-is |
|---|---|---|---|
| Stageshow | A specialized skill anchors on one thesis and names failure modes; the package includes a runtime kit, reusable gold examples, explicitly bad/good teaching pairs, reference sheets, a local playground, capture/film scripts, state/width gates, and a human visual review step. | Each weight-space skill should remain narrow and bundle the exact reference, script, asset/template, and scenario fixtures needed for its handoff. Static checks and model-behavior review remain separate. | A React kit, visual gold scenes, and browser-film gates do not fit checkpoint workflows. |
| Superpowers | Treats skill edits as TDD: run pressure scenarios without the skill, observe the exact violation/rationalization, write the minimum instruction, run the same scenarios with the skill, then close newly observed loopholes. Includes no-skill controls, fresh contexts, repeated micro-tests, and human review of flagged outcomes. | For behavioral changes, require before/after evidence from the same scenario set. Our `skill_eval.py` prepares and scores records but does not execute agent sessions; an eval fixture or green CI is not a behavioral pass. | Mandatory subagents and its specific runtime paths are not portable assumptions. |
| gstack | Separates a top-level router from specialized skills; uses curated phrase triggers and deterministic scoring with explain/dry-run output; adds optional host hooks for routing and stop-time output contracts; defines explicit per-skill contract item types; tracks hook decisions without logging prompt text; adds opt-in gates and switch precedence; uses locked per-task evals, calibration, multiple trials, spend caps, per-task regression and safety policies; checks skill-to-tool drift and skill size. | Use an explicit router and activation matrix; define checkable inputs/outputs and stage gates; keep route decisions explainable; test per-case regressions and safety cases; add drift and size checks only when the repository has a sustainable measurement baseline. | Do not make Claude Code hooks or nonstandard frontmatter required for portable Agent Skills. Do not route every skill on a broad keyword scan: gstack's own routing docs describe false-positive reduction after limiting the routed set. |
| Matt Pocock's `grill-me` | Separates a human-only entry-point wrapper from the shared model-invoked interview primitive. The primitive models a decision tree, asks independent questions in rounds, has the agent look up facts, waits for the user's decisions, and requires confirmation before action. | Use the same separation when a future experiment-planning interview becomes substantial: a clear entry point can invoke a reusable goal-clarification primitive. Continue direct fact-finding where tools/files can answer. | Do not add a wrapper/core pair for a simple one-step goal form; it would add indirection without reuse. |

## Routing policy for Weight Space Workbench

The routing matrix is maintained in [the `wsp-loop` routing reference](../.agents/skills/wsp-loop/references/routing.md). In short: broad weight-change requests enter `wsp-loop`; focused requests enter the matching stage; conceptual questions are answered directly; the earliest unmet prerequisite wins; explicit invocation narrows scope but cannot waive gates; release stays user-requested.

This is the behavior that was missing from the earlier project review. The descriptions alone were not a complete routing policy, and there was no clear rule for adding a new skill route. The new reference defines both.

## Contract boundary

The repository has several useful contract pieces already: stage handoffs in `docs/WORKFLOW.md`, JSON assets, and validators for goal contracts, run records, and release bundles. They are not equivalent to gstack's stop hook. Current validation is explicit CLI validation, not automatic interception of an agent's final answer. Cross-host skill portability remains the default; a future host adapter must be optional and must make absence of the hook visible.

For each stage, the intended contract is:

- **Inputs:** concrete prerequisite artifact paths and identifiers.
- **Output:** one named artifact, or an explicit blocked/no-edit/inconclusive result.
- **Validation:** a bundled deterministic check where schema or integrity can be mechanically tested.
- **Human judgment:** causal hypotheses, metric meaning, license interpretation, and safety claims stay reviewable and cannot be certified by schema validation.

## Gaps that remain after this documentation change

1. `skill_eval.py` does not launch agents, calibrate which skill was loaded, repeat trials, lock eval tasks, estimate cost, or enforce per-case non-regression/safety policy. It only prepares paired records and validates grades supplied by the evaluator.
2. There is no automatic prompt router, machine-readable route registry, or host hook. The new routing reference is human/agent guidance; add a deterministic `--explain` router only after false-positive and false-negative scenarios are measured.
3. There is no transcript stop hook. A missing final artifact is caught only when the user/operator runs the relevant validator.
4. No behavior runs have yet established whether each skill triggers correctly or improves compliance. The eight eval suites are scenarios, not passing results.
5. No skill-size ratchet or installed-resource drift check exists. Before adding those, establish what is measured, which generated/rendered files are canonical, and a non-flaky CI gate.

## Adoption order

1. Freeze positive and near-miss routing prompts for each skill and run them in the actual supported clients.
2. Improve the eval contract to include `none`, repeated trials, calibration, immutable task locks, incomplete/error states, and safety/per-case regression rules before claiming skill effectiveness.
3. Add the skill route to the README and router reference whenever a new skill is approved; require activation and non-activation eval cases in that same change.
4. Add optional host-specific enforcement only after documenting host support, failure behavior, enable/disable precedence, privacy-safe records, and the portable manual fallback.
5. Add skill size and dependency-drift ratchets after collecting a stable baseline and defining the repair path for each finding.

## Sources reviewed

- [Stageshow skill](https://github.com/benjitaylor/skills/blob/main/stageshow/SKILL.md), [package README and verification](https://github.com/benjitaylor/skills/blob/main/stageshow/README.md)
- [Superpowers writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)
- [gstack routing and contracts](https://github.com/garrytan/gstack/blob/main/docs/skill-routing-and-contracts.md), [skill gates](https://github.com/garrytan/gstack/blob/main/docs/skill-gates.md), [skill eval contract](https://github.com/garrytan/gstack/blob/main/docs/designs/SKILL_EVAL_CONTRACT.md), [skill inventory and `/write-skill` notes](https://github.com/garrytan/gstack/blob/main/docs/skills.md)
- [Matt Pocock's `grill-me`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md), [shared `grilling` skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)
