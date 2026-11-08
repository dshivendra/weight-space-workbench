# Security policy

## Scope

Report security issues in the scripts or workflow through a private GitHub Security Advisory when available. Do not include secrets, private checkpoints, or personal data in a public issue.

## Safety boundaries

- Utilities write candidate artifacts to a new path and should not overwrite source checkpoints.
- Inspect scripts before running them on valuable or restricted model artifacts.
- Treat model files, tensor names, user-supplied paths, and evaluation outputs as untrusted input.
- This project does not certify a model as safe for deployment. Physical robot use requires a separate safety case, simulation, controls, and human oversight.
