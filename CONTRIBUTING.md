# Contributing

Thanks for helping improve Weight Space Workbench.

## Contributions

- Keep each skill focused on one clear task and usable without relying on hidden project context.
- Preserve the standard `SKILL.md` frontmatter (`name`, `description`) and progressive-disclosure pattern.
- Separate verified behavior from hypotheses. Avoid claims that a raw weight pattern proves a model capability.
- Keep model edits explicit, bounded, reversible, and tied to a pinned checkpoint.
- Never add model weights, private data, tokens, or credentials to the repository.
- Include a concise example and expected output for new scripts or workflows.

## Change process

1. Describe the behavior or gap being addressed.
2. Make the smallest focused change.
3. Run the repository's documented validation commands that apply to the change.
4. Include evidence and limitations in the pull request description.

## Skill format

Follow the current Agent Skills specification at <https://agentskills.io/specification>. Keep each skill's trigger description precise and its instructions operational. Put optional material in `references/` instead of expanding the main instruction file unnecessarily.
