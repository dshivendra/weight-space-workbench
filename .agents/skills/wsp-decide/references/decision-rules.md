# Decision rules

- **Keep:** preregistered primary threshold passes, all guardrails pass, paired uncertainty supports the claim, frozen holdout supports transfer, and provenance is complete.
- **Revert:** primary criterion fails, any guardrail fails, unexpected behavior appears, or artifacts cannot be reproduced.
- **Inconclusive:** sample size, uncertainty, holdout, or provenance is insufficient to distinguish improvement from noise.

Do not rewrite the threshold, guardrails, split, or uncertainty procedure after seeing candidate results. A changed experiment is a new run with a new ID. The bundled comparator performs threshold arithmetic and enforces a caller-supplied uncertainty status; it does not compute statistics or assess the quality of a protocol.
