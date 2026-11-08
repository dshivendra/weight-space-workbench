# Baseline reproducibility record

Record the exact revision of the model, evaluator, dataset, and environment. A branch name or mutable `main` tag is not an immutable revision.

Include framework and dependency versions, hardware/device, dtype, batch size, inference settings, preprocessing and normalization, seed(s), sample count, and any nondeterministic operations. Record raw outputs or a privacy-safe stable reference to them.

For stochastic models, repeat the baseline under the preregistered seeds. Keep each run's metrics and aggregate uncertainty; do not select the best seed. The bundled hash script hashes file contents only and does not prove a dataset's semantic correctness or a model's identity.
