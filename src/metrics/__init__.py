"""Evaluation metrics for state-space reasoning tasks."""

from deterministic_horizon.metrics.ssj import compute_ssj, SSJResult
from deterministic_horizon.metrics.sfe import compute_sfe, SFEResult
from deterministic_horizon.metrics.statistics import (
    accuracy_by_depth,
    estimate_horizon,
    cross_model_correlation,
    bootstrap_ci,
    compute_effect_size,
    fit_decoherence_model,
)

__all__ = [
    "compute_ssj",
    "SSJResult",
    "compute_sfe",
    "SFEResult",
    "accuracy_by_depth",
    "estimate_horizon",
    "cross_model_correlation",
    "bootstrap_ci",
    "compute_effect_size",
    "fit_decoherence_model",
]
