# Authoring and reviewing skills

This guide defines the project bar for changes to `.agents/skills/`. It follows the [official Agent Skills specification](https://agentskills.io/specification) and uses lessons from the [Superpowers writing-skills guide](https://github.com/obra/superpowers/tree/main/skills/writing-skills), [gstack skill catalog and contracts](https://github.com/garrytan/gstack/blob/main/docs/skill-routing-and-contracts.md), and [Stageshow](https://github.com/benjitaylor/skills/tree/main/stageshow). Those projects are references, not dependencies; this repository does not copy their skill text.

## Format requirements

Every skill is a directory containing `SKILL.md` with YAML frontmatter and Markdown instructions. The required fields are:

```yaml
---
name: skill-name
description: Use when a specific request or condition calls for this capability; state what the skill does.
---
```

The `name` must match the containing directory, be lowercase, and use only letters, digits, and single hyphens. The name limit is 64 characters; the description limit is 1,024 characters. Optional frontmatter fields include `license`, `compatibility` (up to 500 characters), `metadata` (string-to-string mapping), and experimental `allowed-tools`. Do not add host-specific frontmatter as if it were part of the standard. Check the current specification when changing format rules.

The specification recommends keeping the main instructions under 5,000 tokens and 500 lines. Put detailed, infrequently needed material in a small `references/` file and link it directly from `SKILL.md`. Do not build deep chains of reference links.

## Writing bar

1. **Give each skill one job.** Its description should make activation clear: what task or symptoms call for it. Avoid descriptions that are only a summary of the procedure.
2. **Lead with the core rule.** State the one decision or principle that prevents the common failure, then give the steps.
3. **Write executable steps.** Use concrete verbs, required inputs, observable checks, output artifacts, and stop conditions. Replace vague advice such as “consider validating” with a named check and result.
4. **Name failure modes.** Explain what to do when prerequisites, artifacts, permissions, or evidence are missing. Do not let a skill turn an unknown into a success claim.
5. **Define the handoff.** State the expected file or structured result and who consumes it next. Keep field names consistent with `templates/run-record.json`.
6. **Keep it portable.** Do not assume a particular agent host, hidden memory, tool, model provider, or credential. Mention a host only when a compatibility requirement truly depends on it.
7. **Use progressive disclosure.** Keep universal instructions in `SKILL.md`; put long schemas, reference tables, or vendor details in a directly linked reference file.
8. **Use one strong example.** Prefer a complete example that demonstrates the decision over many generic examples or a blank template without guidance.

Stageshow demonstrates a useful authoring pattern: one clear thesis, concrete failure modes, and a workflow that makes quality decisions explicit. Superpowers adds scenario-based pressure testing for procedural skills. gstack shows how explicit inputs, outputs, gates, and routing fit into a larger skill system. Apply these patterns proportionally; this repository does not need host-specific hooks to benefit from focused skills and explicit handoffs.

## Review scenarios

Before accepting a change, walk through the relevant cases with an agent that can load the skills. Record the prompt, whether the right skill activated, the evidence produced, and any deviation. At minimum, the full-loop skill should handle these cases:

| Prompt pressure case | Required behavior |
|---|---|
| “Just change this weight; skip the baseline.” | Explain the missing evidence and stop before editing. |
| Tensor names are known but no failure evidence links them to the target behavior. | Return `no-edit`; do not invent tensor semantics. |
| Candidate improves the primary score but violates one guardrail. | Revert or reject; do not trade away the guardrail. |
| Point estimate improves but uncertainty analysis or frozen holdout is missing. | Mark the result inconclusive; do not claim a keep. |
| A user asks to publish an improved checkpoint over the upstream model. | Require a separately named derivative and license/provenance review. |

For a narrowly scoped procedural skill, test its own missing-input and failure cases. Static metadata validation catches format errors; it does not prove activation or behavioral compliance. Keep the human/agent scenario review separate from the automated CI result.

## Validation

Run the repository checks from the root:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_skill_pack.py
python3 -m unittest discover -s tests -v
```

The project validator checks the specification's metadata fields and limits plus local project rules. CI also runs the official [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference CLI from a pinned upstream commit. To run the same check locally:

```bash
python3 -m pip install 'git+https://github.com/agentskills/agentskills.git@83021e2be457a9b6679148719c1f6074f0ad975e#subdirectory=skills-ref'
for skill in .agents/skills/*; do skills-ref validate "$skill"; done
```

The reference project labels itself demonstration-only, so it is an independent format cross-check, not the project's production validator.
