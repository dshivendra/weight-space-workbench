# Supported formats and boundaries

## Included editor

`scripts/apply_safetensors_delta.py` targets a single `.safetensors` file readable by `safetensors.torch`. It can change one explicitly named floating-point scalar by a bounded delta and saves a new file plus a JSON receipt. It preserves Safetensors metadata when present.

The script loads the full checkpoint into CPU memory. Plan for memory above the checkpoint size because loading and reserializing tensors requires additional memory. It is not an in-place or sharded-checkpoint editor.

## Not handled by the bundled editor

- JAX/Flax/Orbax or Octo `.msgpack` checkpoints
- PyTorch sharded/distributed checkpoints
- Quantized or packed tensors requiring specialized kernels
- LoRA/PEFT adapter merges
- Tensor-parallel or pipeline-parallel checkpoint layouts
- Model-specific normalization, tokenizer, image processor, or action-stat updates

For these, use the framework's supported checkpoint APIs and implement an adapter that retains source immutability, bounded edits, exact provenance, a load check, and model-specific evaluation.

## Evaluation is model-specific

The project does not ship a universal evaluator. A valid evaluator must use the model's expected inputs, preprocessing, task/environment, and output interpretation. A generic action MSE or classification accuracy can miss regressions in task success, calibration, latency, or safety constraints.
