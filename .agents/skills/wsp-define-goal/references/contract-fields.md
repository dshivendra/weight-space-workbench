# Experiment contract fields

A contract is a preregistration artifact. Fill it before running an edit or looking at candidate holdout results.

- **Goal:** a concrete input/output behavior, with one or more examples of the baseline failure.
- **Model identity:** repository and immutable revision; checkpoint hash when locally available; architecture and license only when confirmed.
- **Evaluation context:** offline, simulator, or hardware; name the simulator/robot and its action constraints when applicable.
- **Primary metric:** one named measure, optimization direction, aggregation, minimum meaningful change, and uncertainty procedure.
- **Guardrails:** independent failure limits. A primary gain never offsets a failed safety or regression limit.
- **Data protocol:** dataset revision, split, preprocessing, sample IDs or deterministic selection, and seed policy.
- **Stop/rollback:** explicit events that stop editing or reject the candidate.

Unknown values stay `unknown`; avoid substituting assumptions. Change a preregistered value only by creating a new version with a reason before observing the result it affects.
