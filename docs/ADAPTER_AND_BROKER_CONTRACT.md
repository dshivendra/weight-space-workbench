# Broker and adapter contract

This document defines the target boundary for architecture-independent weight-space programming and records the current adapter's actual limits. A capability declaration is descriptive until an isolated broker mediates every artifact read and write; a manifest by itself is not a security boundary.

## Trust boundary

The agent submits typed requests to the broker. The broker owns artifact handles, policy evaluation, candidate materialization, probe budgets, commit authority, and the audit log. Adapters translate broker operations into format/runtime-specific behavior. Agents must not receive artifact-store credentials, writable checkpoint paths, or unrestricted access to the process that owns model files.

If agents can execute arbitrary code as the same user that runs the editor, they can bypass a local CLI gate. A deployment claiming hard enforcement must isolate the agent and broker with an OS or service boundary and expose only broker operations to the agent.

## Capability negotiation

At workspace creation, the broker intersects the operation sets from its own implementation, the selected adapter, the artifact manifest, and the active policy:

```text
negotiated = broker_operations
           ∩ adapter_operations
           ∩ artifact_operations
           ∩ policy_operations
```

The broker rejects an unsupported operation before allocating the candidate or calling an adapter. It must not infer capabilities from a file extension, architecture name, or a caller-supplied claim. Capability descriptors are versioned inputs and their canonical digest is attached to each workspace and ledger event.

`adapters/safetensors-local-v1/capabilities.json` describes the bundled editor's narrow profile. It allows metadata and bounded reads plus one scalar-delta candidate and digest/receipt verification. It explicitly does not advertise model execution, graph inspection, quantized or sharded edits, tied-parameter awareness, canonical commit, or publishing.

## Address resolution

An address resolves to one canonical storage target and may return multiple logical aliases. The adapter must report alias semantics and the full set of affected addresses before an edit is staged. If aliases or write propagation cannot be determined, the adapter rejects the edit. The current single-file Safetensors profile does not prove that the tensors are semantically tied in a loaded model; it therefore declares tied-parameter awareness unsupported.

## Transaction boundary

The canonical artifact is immutable during inspection, editing, and candidate evaluation. A candidate is created under a new immutable identity and is bound to its base digest, adapter descriptor digest, operation hash, and policy digest. Candidate regression and guardrail checks must pass before the broker atomically advances a canonical pointer using compare-and-swap. A failed compare-and-swap aborts the commit; it must not silently rebase.

The local editor currently creates a candidate and receipt only. It does not evaluate model behavior, commit a canonical pointer, run regressions, or publish. A receipt is evidence of a file transformation, not evidence of model improvement.

## Adapter requirements

Each adapter must declare supported artifact formats, address schemes, operations, runtime targets, and limits. For each operation it implements, it must also provide:

- Typed input and output schemas, including representation domain and shape/layout rules.
- Address resolution and alias behavior.
- Preconditions, postconditions, and a machine-readable diff.
- Determinism class for transformation and execution separately.
- Candidate materialization and integrity verification behavior.
- Explicit unsupported behavior that fails closed.

Quantized adapters must distinguish packed-code edits from dequantized-value edits and report realized reconstruction error. Sharded adapters must address logical tensors and provide an all-shards-or-none commit protocol. Graph migrations such as subgraph replacement or parameter insertion require a distinct migration contract and elevated approval; they are not ordinary tensor edits.

## Commit sequence

```text
negotiate -> inspect -> draft -> validate -> materialize candidate
          -> invariant checks -> candidate probes/regressions -> stage
          -> compare-and-swap commit -> verify -> export or publish
```

The canonical pointer advances only after candidate checks and required approvals pass. A post-commit verification failure may trigger a recorded rollback, but rollback is an exception path. All state changes, rejections, and recovery actions are append-only audit events.

## Capability status

| Capability | Bundled local adapter |
|---|---|
| Single-file Safetensors metadata and bounded reads | Supported by helper tools |
| One bounded floating-point scalar delta to a new file | Supported |
| Candidate SHA-256 and edit receipt | Supported |
| General typed parameter-address broker | Not implemented |
| Agent/broker process isolation | Not implemented |
| Model execution and behavioral probes | Not implemented |
| Candidate regression and uncertainty evaluation | Separate helpers; not broker-attested |
| Transactional canonical commit or rollback | Not implemented |
| ONNX, GGUF, PyTorch, sharded, or quantized adapters | Not implemented |
| Graph migration and tied-parameter semantics | Not implemented |

The table describes current repository capability, not a claim that the target broker contract is already enforced end to end.
