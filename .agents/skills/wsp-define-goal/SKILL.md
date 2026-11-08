---
name: wsp-define-goal
description: "Use before a neural-network baseline, weight edit, or fine-tuning comparison. Convert the requested behavior into a measurable contract with a target metric, guardrails, data splits, and stop conditions."
license: MIT
metadata:
  version: "0.3.0"
  category: machine-learning
---

# Define the experiment goal

Create a concise contract before touching weights.

## Capture

- **Behavior:** Describe the specific observed failure and desired behavior with examples where possible.
- **Model:** Identify repository, immutable revision, framework, checkpoint format, architecture, and license.
- **Context:** State whether evaluation is offline, simulated, or physical; name the robot/environment when relevant.
- **Primary metric:** Choose one measurable metric and direction (`lower` or `higher`).
- **Guardrails:** List metrics that must not regress, including safety constraints for action models.
- **Data:** Pin data identity, preprocessing, train/validation/test split, and seed policy.
- **Acceptance:** Declare minimum improvement, uncertainty method, rollout count if needed, and rollback condition.
- **Limits:** State compute, network, data-access, and privacy restrictions.

## Rules

- If the target or evaluation protocol is ambiguous, ask only for the missing decision that materially changes the experiment; continue independent discovery work.
- Do not promise that changing a parameter will improve behavior.
- Keep evaluation data held out from edit selection.
- Distinguish direct weight editing from optimizer-based fine-tuning in the contract.
- For robot policies, forbid live hardware as the first evaluation stage.

## Output

Write `goal.json` using `assets/goal-contract.json`. If the full repository is checked out, you may also fill the matching task fields in `templates/run-record.json`. Mark unknown values explicitly as `unknown`; never invent model or dataset details.

## Supporting files

- Run `python3 scripts/validate_goal_contract.py CONTRACT.json` before collecting a baseline.
- Use `assets/goal-contract.json` as the portable output skeleton; fill unknowns explicitly.
- Read `references/contract-fields.md` when deciding what evidence belongs in each contract field.
- Review `evals/evals.json` for the ambiguous-goal and missing-baseline cases this skill must handle.
