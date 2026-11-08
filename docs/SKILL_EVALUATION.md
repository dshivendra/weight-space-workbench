# Skill behavior evaluation

The per-skill `evals/evals.json` files define scenarios, expected outcomes, and assertions. They are evaluation fixtures, not evidence that a skill has passed. This helper prepares paired runs and validates human- or agent-graded results; it does not launch an agent or decide whether a skill is good.

## Evaluation protocol

1. Pin the skill revision, model, agent host/runtime, tool permissions, and evaluation files. Keep the eval suite frozen during the comparison.
2. Prepare a workspace from the exact candidate package:

   ```bash
   python3 scripts/skill_eval.py prepare .agents/skills/wsp-define-goal \
     --output /tmp/wsp-define-goal-eval.json
   ```

   The default baseline is `without_skill`. For a version comparison, pass `--baseline previous_version --baseline-skill /path/to/old-skill-snapshot`; the snapshot must have the same skill name and different package contents.
3. For each case, start independent clean agent sessions with the same model, system context, tools, and user prompt. In the candidate session, make the candidate skill available; in the baseline session, omit the skill or provide the previous snapshot. Give the agent only `prompt` and the declared `files`. Do not reveal `expected_output`, assertions, or grading guidance to the agent. Avoid sharing conversation state between runs.
4. Save each complete response and relevant execution trace as a durable artifact. Fill `output_ref`, `duration_ms`, `total_tokens` when available, and grade every assertion against that saved artifact. A pass or fail needs concise, specific evidence. Do not infer an assertion from intent or from the skill text alone. Use the same grader and rubric for both conditions.
5. Preserve any `review_notes`, including ambiguous cases, tool failures, and deviations. Generate the report:

   ```bash
   python3 scripts/skill_eval.py report .agents/skills/wsp-define-goal \
     --results /tmp/wsp-define-goal-eval.json \
     --output /tmp/wsp-define-goal-report.json
   ```

6. Review regressions and all guardrail assertions before changing the skill. If improving the skill, change one meaningful thing at a time and rerun the same frozen cases. Add new cases for newly discovered failure modes; do not silently tune the test set to the candidate.

## Workspace fields

`prepare` writes a JSON workspace with one `with_skill` and one `baseline` run per fixture. `expected_output` and assertion strings are included for the grader only. Results are tied to the candidate package hash and skill version; if the package changes, prepare a fresh workspace. In a previous-version comparison, record the old snapshot hash and version. `report` rejects missing or duplicate runs, missing outputs, ungraded assertions, missing evidence, and stale candidate packages.

Durations and token counts are optional because some clients do not expose them. If present, they must be finite, non-negative values. The report calculates per-condition assertion and whole-case pass rates plus available mean duration and token count, then reports candidate-minus-baseline deltas. It does not calculate statistical uncertainty, control model nondeterminism, verify output references, or adjudicate evidence quality.

## Interpreting results

A positive score delta is descriptive for the tested prompts, model, host, and runtime only. It is not a universal skill-quality score and does not prove reliable activation, causal improvement, or safety. Review the saved outputs and traces, prompt coverage, individual guardrails, grader consistency, and repeated-run variability before drawing a conclusion. For high-impact skills, run multiple independent trials and report uncertainty separately. Keep behavior review distinct from repository static checks and CI.

The helper has no external dependencies and can be checked with:

```bash
python3 -m unittest tests/test_skill_eval_harness.py -v
```
