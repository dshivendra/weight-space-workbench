---
name: wsp-define-goal
description: "Use before a neural-network baseline, weight edit, or fine-tuning comparison. Convert the requested behavior into a measurable contract with a target metric, guardrails, data splits, and stop conditions."
license: MIT
metadata:
  version: "0.2.0"
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

Write `goal.json` using the matching fields in `templates/run-record.json`, or summarize the same fields in the run record. Mark unknown values explicitly as `unknown`; never invent model or dataset details.
