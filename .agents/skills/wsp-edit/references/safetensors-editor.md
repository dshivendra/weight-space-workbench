# Safetensors editor contract

The bundled editor accepts one `.safetensors` file and edits one explicitly named floating-point scalar. It requires a source SHA-256, tensor name, coordinate, expected old value, delta, maximum absolute delta, and two new output paths. It rejects stale source/value expectations and does not overwrite existing output paths.

Install the optional dependencies with `python3 -m pip install -r requirements-safetensors.txt` from the repository, or install compatible `torch` and `safetensors` packages in the target environment. The source remains immutable; candidate and receipt are written separately and include content hashes.

This is a file-integrity tool, not a model-specific loader or evaluator. Reload the candidate through the model's own code and run a forward smoke check before scoring it. It does not support sharded checkpoints, optimizer updates, fine-tuning, quantized formats, or format conversion.
