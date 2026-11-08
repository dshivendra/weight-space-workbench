---
name: wsp-release
description: "Package a validated weight-edit derivative with model/data/evaluator provenance, license review, model card changes, and reproducible results. Use only after the keep decision and when the user requests publication or release."
metadata:
  version: "0.1.0"
  category: machine-learning
---

# Release a derivative checkpoint

1. Confirm the decision is `keep` and all required evidence exists.
2. Check the upstream model and dataset licenses and redistribution terms. Do not publish private or restricted artifacts.
3. Publish to a new repository or branch controlled by the user; never overwrite upstream weights.
4. Include base model ID/revision, exact edit receipt, evaluator/data revisions, metrics and limitations, runtime requirements, and intended use.
5. Include the model configuration and required preprocessing/processor files so the checkpoint is loadable.
6. Record a release checksum and immutable commit/revision. Verify the published artifact can be downloaded and loaded if network access permits.
7. Clearly label the release as a research derivative. Do not describe offline metrics as proof of physical safety.

If publishing credentials or repository access are unavailable, prepare the release directory and provide the exact upload command without claiming publication succeeded.
