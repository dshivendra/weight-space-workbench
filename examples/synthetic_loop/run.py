#!/usr/bin/env python3
"""Run a transparent direct-weight-edit demonstration on synthetic data."""

from __future__ import annotations

import json

import numpy as np


def main() -> None:
    rng = np.random.default_rng(42)
    # Simplified perception outputs and an instruction feature.
    x = np.column_stack((
        rng.uniform(-1, 1, 64),  # object_x from the image
        rng.uniform(-1, 1, 64),  # target_x from the image
        np.ones(64),  # language command: "move object to target"
    ))
    y = (x[:, 1] - x[:, 0]).reshape(-1, 1)

    # The baseline policy has the wrong/incomplete object-position coefficient.
    weights = np.array([[0.0, 1.0, 0.0]], dtype=np.float64)

    def mse(candidate: np.ndarray) -> float:
        prediction = x @ candidate.T
        return float(np.mean((prediction - y) ** 2))

    before = weights.copy()
    baseline_mse = mse(weights)

    # Hypothesis: displacement requires subtracting the object's current position.
    weights[0, 0] = -1.0
    candidate_mse = mse(weights)

    report = {
        "model": "synthetic linear image+instruction-to-action policy",
        "examples": len(x),
        "edit": {"tensor": "action_dx.weight", "index": [0, 0], "before": float(before[0, 0]), "after": float(weights[0, 0])},
        "parameters_changed": int(np.count_nonzero(weights != before)),
        "baseline_mse": baseline_mse,
        "candidate_mse": candidate_mse,
        "mse_reduction_percent": 100.0 * (baseline_mse - candidate_mse) / baseline_mse,
        "interpretation": "Synthetic proof of the measurement loop only; the coefficient was derived from the known target equation.",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
