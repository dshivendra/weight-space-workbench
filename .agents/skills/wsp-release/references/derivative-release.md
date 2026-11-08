# Derivative checkpoint release checklist

Before publishing, verify the upstream model and dataset license terms allow redistribution of the artifact and the planned use. Keep attribution and notices. Do not publish private data, credentials, restricted outputs, or a checkpoint whose provenance is unknown.

Package the derivative with a complete configuration/processor, base model ID and immutable revision, exact edit receipt, dataset and evaluator revisions, reproducible metrics, limitations, intended use, and checksum. Use a new repository or clearly named derivative branch; never replace upstream files.

A `keep` decision is not a safety certification. State whether validation was offline, simulated, or physical and do not generalize beyond that evidence.
