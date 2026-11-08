# Weight Space Workbench

Portable Agent Skills and small utilities for controlled, auditable weight-space experiments.

This project helps an agent and researcher move from a model-behavior goal to a reproducible weight edit, evaluation, and keep-or-revert decision. It is inspired by role-based engineering workflows such as gstack, but the skills and utilities here are original and focused on model weight experiments.

> **Research tooling, not an optimizer or safety certification.** A metric improvement on a benchmark does not establish general improvement or safe physical behavior. Run robotics policies in simulation first; use human-supervised, bounded tests before any hardware deployment.

## Workflow

```text
Define goal → Pin model/data/evaluation → Measure baseline → Diagnose failure
           → State weight-edit hypothesis → Edit a copy → Integrity checks
           → Evaluate same + held-out data → Compare guardrails → Keep or revert
```

The skills follow the [Agent Skills specification](https://agentskills.io/specification): each skill is a directory with a `SKILL.md` containing YAML frontmatter and task instructions. Install only the skills you want into a compatible agent's skill directory.

## Included skills

| Skill | Responsibility |
|---|---|
| `wsp-loop` | Orchestrate the full experiment and enforce evidence at every transition. |
| `wsp-define-goal` | Turn a vague request into a measurable behavior contract and guardrails. |
| `wsp-baseline` | Pin the model, data, preprocessing, evaluator, and baseline metrics. |
| `wsp-inspect` | Inspect architecture and weights without overclaiming what weights reveal. |
| `wsp-edit` | Propose and apply a bounded edit to a copy of a Safetensors checkpoint. |
| `wsp-evaluate` | Run controlled same-set and holdout evaluation with relevant safety metrics. |
| `wsp-decide` | Apply preregistered acceptance rules; keep, revert, or run a new hypothesis. |
| `wsp-release` | Package provenance and publish a validated derivative without overwriting upstream. |

## Quick start

### 1. Install the skill pack

Clone this repository, then copy `.agents/skills/` into the skills directory used by your agent. For Codex CLI, Claude Code, and other compatible clients, use the skill installation method documented by that client. Each skill is independently usable; start with `wsp-loop` for the end-to-end workflow.

If your client scans an arbitrary skill directory, the helper can copy the pack there without overwriting existing folders:

```bash
python scripts/install_skills.py --destination /path/to/agent/skills
```

### 2. Try the offline example

The synthetic example needs Python and NumPy only. It changes one coefficient in a tiny vision/text-to-action policy, evaluates on fixed examples, and prints a before/after report:

```bash
python examples/synthetic_loop/run.py
```

This example is intentionally transparent and is **not** evidence that an LLM can infer useful edits in a pretrained model.

### 3. Apply a one-scalar edit to a Safetensors copy

Install the optional dependency and edit into a new destination (the utility refuses to overwrite an existing path):

```bash
python -m pip install safetensors torch
python scripts/apply_safetensors_delta.py \
  --source model.safetensors \
  --destination artifacts/candidate/model.safetensors \
  --tensor 'policy.action_head.weight' \
  --index 0,3 \
  --delta -0.001 \
  --max-abs-delta 0.01
```

This utility changes exactly one scalar and writes an edit receipt next to the destination. It does not infer tensor semantics, guarantee the checkpoint remains behaviorally sound, or evaluate the model. Run the model-specific loader and evaluator after editing.

## Structural validation

```bash
python scripts/validate_skill_pack.py
```

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for stage contracts and [docs/SUPPORTED_FORMATS.md](docs/SUPPORTED_FORMATS.md) for framework limitations.

## Evaluation discipline

- Pin an immutable upstream revision and record hashes for model, data, and evaluation code.
- Decide the primary metric, minimum gain, regression metrics, and stopping rule before editing.
- Keep model preprocessing and evaluation settings fixed between baseline and candidate.
- Use paired examples plus a fresh held-out split; report sample counts and uncertainty where possible.
- For robotics, include task success, action error, constraint violations, and rollout failures. Do not infer real-world safety from offline action loss alone.
- Save every attempted edit. Revert if the target gain is absent, guardrails fail, or the result does not repeat.
- Do not upload private weights, sensitive data, or checkpoints whose license does not permit redistribution.

## Repository layout

```text
.agents/skills/     Portable Agent Skills
docs/               Workflow and design notes
examples/           Fully transparent synthetic demonstration
scripts/            Narrow, auditable utilities
templates/          Run-record and edit-manifest templates
```

## License and attribution

Project code and original skill content are MIT licensed. Agent Skills is an open format; this repository is an independent implementation and is not affiliated with Anthropic, OpenAI, Hugging Face, Garry Tan, or gstack. See [LICENSE](LICENSE).
