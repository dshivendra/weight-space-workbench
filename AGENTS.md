# Repository guidance

## Scope

This repository contains portable Agent Skills and small utilities for controlled weight-space experiments. Keep it focused on reproducibility, bounded edits, honest evidence, and model-specific evaluation.

## Skill authoring

- Put each skill in `.agents/skills/<skill-name>/SKILL.md`.
- Keep YAML frontmatter `name` identical to the folder name; write a precise `description` that makes activation conditions clear.
- Keep core instructions operational and load extra material only when needed.
- Never imply raw weight inspection proves semantics or that one scalar edit establishes a model improvement.

## Model artifacts

- Never commit model weights, private datasets, access tokens, or generated checkpoints.
- The included edit utility supports one scalar in a single Safetensors file; do not advertise support for other formats without an adapter and model-load/evaluation path.
- Keep source checkpoints immutable and write candidates to new paths.
- Report actual execution separately from plans, examples, and hypothetical results.

## Open source hygiene

- Keep scripts narrow, readable, and explicit about dependencies.
- Record model and dataset licenses before redistribution.
- Preserve original upstream attribution and do not copy third-party skill text.
