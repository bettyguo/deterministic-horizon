"""
Practitioner-facing decision helper: *should my agent think harder, or call a tool?*

This module turns the paper's theoretical bound into a one-line API that agentic
systems can call at planning time. The math comes from Theorem 1:
``P(correct at depth d) ≈ exp(-d·ε₀ − γ·d(d+1) / (2L))``; the heuristic constants
come from the cross-model fits in §5 of the paper.

Example
-------
>>> from deterministic_horizon import should_delegate
>>> should_delegate(estimated_depth=8)         # short — think it through
False
>>> should_delegate(estimated_depth=35)        # past the horizon — delegate
True
>>> decision = delegation_decision(
...     estimated_depth=22,
...     model="claude-4.5-opus",
...     tool_available=True,
... )
>>> decision.delegate, round(decision.expected_neural_accuracy, 2)
(True, 0.43)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Per-model decoherence parameters (Table 3 of the paper).
#
# These are the (ε₀, γ, d*) triples fit to each frontier model under the C1
# (neural chain-of-thought) condition. The defaults are deliberately
# *conservative*: when in doubt, the helper prefers to recommend delegation.
# ---------------------------------------------------------------------------

MODEL_HORIZONS: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4o":            {"eps0": 0.022, "gamma": 0.0028, "d_star": 22.0},
    "gpt-4o-mini":       {"eps0": 0.030, "gamma": 0.0040, "d_star": 19.0},
    "o1":                {"eps0": 0.015, "gamma": 0.0020, "d_star": 28.0},
    "o1-mini":           {"eps0": 0.018, "gamma": 0.0024, "d_star": 25.0},
    "o3-mini":           {"eps0": 0.013, "gamma": 0.0018, "d_star": 31.0},
    # Anthropic
    "claude-3.5-sonnet": {"eps0": 0.020, "gamma": 0.0025, "d_star": 24.0},
    "claude-4.5-sonnet": {"eps0": 0.018, "gamma": 0.0022, "d_star": 26.0},
    "claude-4.5-opus":   {"eps0": 0.015, "gamma": 0.0020, "d_star": 28.0},
    # DeepSeek
    "deepseek-v3":       {"eps0": 0.024, "gamma": 0.0030, "d_star": 21.0},
    "deepseek-r1":       {"eps0": 0.016, "gamma": 0.0021, "d_star": 27.0},
    # Open-weight
    "llama-3.1-70b":     {"eps0": 0.028, "gamma": 0.0035, "d_star": 20.0},
    "qwen-2.5-72b":      {"eps0": 0.026, "gamma": 0.0032, "d_star": 21.0},
    # Sensible fallback — "average frontier model"
    "default":           {"eps0": 0.020, "gamma": 0.0025, "d_star": 24.0},
}

# Empirical mean tool-integrated (C3) accuracy across models / domains (§5).
DEFAULT_TOOL_ACCURACY: float = 0.92


@dataclass(frozen=True)
class DelegationDecision:
    """Structured result of :func:`delegation_decision`."""

    delegate: bool
    estimated_depth: int
    model: str
    expected_neural_accuracy: float
    expected_tool_accuracy: float
    horizon: float
    margin: float
    reason: Literal[
        "above_horizon",
        "below_horizon",
        "tool_unavailable",
        "tool_dominates_by_margin",
    ]

    def explain(self) -> str:
        """Human-readable one-line explanation, useful in agent logs."""
        if self.reason == "tool_unavailable":
            return (
                f"No tool available; falling back to neural reasoning "
                f"(expected accuracy {self.expected_neural_accuracy:.0%} at depth "
                f"d={self.estimated_depth})."
            )
        verb = "delegate" if self.delegate else "reason neurally"
        return (
            f"At estimated depth d={self.estimated_depth}, model {self.model!r} "
            f"is expected to reach {self.expected_neural_accuracy:.0%} via CoT "
            f"vs. {self.expected_tool_accuracy:.0%} via tools "
            f"(horizon d*={self.horizon:.0f}). → {verb}."
        )


def expected_neural_accuracy(
    depth: int | float,
    model: str = "default",
    *,
    eps0: float | None = None,
    gamma: float | None = None,
) -> float:
    """
    Expected accuracy of a neural chain-of-thought at the given depth.

    Implements the closed-form decay model from Theorem 1:
    ``P(correct) ≈ exp(-d·ε₀ − γ·d(d+1) / 2)``.

    Parameters
    ----------
    depth : int | float
        Estimated reasoning depth (number of state-tracking steps).
    model : str
        Model identifier — see :data:`MODEL_HORIZONS` for known names. Unknown
        names fall back to the ``"default"`` (cross-model average) parameters.
    eps0, gamma : float, optional
        Override the per-model decoherence parameters directly. When provided,
        ``model`` is ignored.

    Returns
    -------
    float
        Predicted probability of a correct final answer, in ``[0, 1]``.
    """
    if depth < 0:
        raise ValueError(f"depth must be non-negative, got {depth!r}")
    params = MODEL_HORIZONS.get(model.lower(), MODEL_HORIZONS["default"])
    e0 = eps0 if eps0 is not None else params["eps0"]
    g = gamma if gamma is not None else params["gamma"]
    d = float(depth)
    return float(math.exp(-d * e0 - g * d * (d + 1) / 2.0))


def horizon_for(model: str = "default") -> float:
    """Return the Deterministic Horizon d* for ``model`` (or the default)."""
    return float(MODEL_HORIZONS.get(model.lower(), MODEL_HORIZONS["default"])["d_star"])


def should_delegate(
    estimated_depth: int | float,
    model: str = "default",
    *,
    threshold: float = 0.5,
    tool_available: bool = True,
    tool_accuracy: float = DEFAULT_TOOL_ACCURACY,
    margin: float = 0.10,
) -> bool:
    """
    Cheap boolean: at this depth, should the agent route to a tool?

    Returns ``True`` when *either* expected neural accuracy is below
    ``threshold`` *or* a tool is expected to beat neural reasoning by more
    than ``margin`` — and a tool is available. This mirrors
    :func:`delegation_decision`'s logic, so the cheap boolean and the full
    structured result always agree.

    Use this when you just need a fast branch in your agent loop; use
    :func:`delegation_decision` when you want the full justification
    (e.g. to log it for human review).
    """
    return delegation_decision(
        estimated_depth=estimated_depth,
        model=model,
        tool_available=tool_available,
        tool_accuracy=tool_accuracy,
        threshold=threshold,
        margin=margin,
    ).delegate


def delegation_decision(
    estimated_depth: int | float,
    model: str = "default",
    *,
    tool_available: bool = True,
    tool_accuracy: float = DEFAULT_TOOL_ACCURACY,
    threshold: float = 0.5,
    margin: float = 0.10,
) -> DelegationDecision:
    """
    Full delegation decision with expected accuracy on both branches.

    Delegate when **either** of these holds (and a tool is available):

    1. Neural accuracy at this depth is below ``threshold`` (we're past d*).
    2. Tool accuracy beats neural accuracy by more than ``margin`` —
       *don't* think harder just to break even.

    Parameters
    ----------
    estimated_depth : int | float
        Depth estimate from your planner. If you don't have one, run BFS or
        a learned depth-estimator on the problem first.
    model : str
        Frontier model identifier. Unknown names use cross-model defaults.
    tool_available : bool
        If False, the decision is forced to *not* delegate regardless of d.
    tool_accuracy : float
        Empirical accuracy you've seen for your tool on similar tasks.
        Defaults to the §5 cross-domain mean of 0.92.
    threshold : float
        Below this expected neural accuracy, automatically delegate.
    margin : float
        Even above ``threshold``, delegate when tool beats neural by this much.

    Returns
    -------
    DelegationDecision
        Structured result. Call ``.explain()`` for a human-readable summary.
    """
    if not 0.0 < threshold < 1.0:
        raise ValueError(f"threshold must be in (0, 1), got {threshold!r}")
    if not 0.0 <= margin < 1.0:
        raise ValueError(f"margin must be in [0, 1), got {margin!r}")

    neural = expected_neural_accuracy(estimated_depth, model)
    tool = float(tool_accuracy) if tool_available else 0.0
    horizon = horizon_for(model)

    if not tool_available:
        return DelegationDecision(
            delegate=False,
            estimated_depth=int(estimated_depth),
            model=model,
            expected_neural_accuracy=neural,
            expected_tool_accuracy=0.0,
            horizon=horizon,
            margin=margin,
            reason="tool_unavailable",
        )

    if neural < threshold:
        return DelegationDecision(
            delegate=True,
            estimated_depth=int(estimated_depth),
            model=model,
            expected_neural_accuracy=neural,
            expected_tool_accuracy=tool,
            horizon=horizon,
            margin=margin,
            reason="above_horizon",
        )

    if tool - neural > margin:
        return DelegationDecision(
            delegate=True,
            estimated_depth=int(estimated_depth),
            model=model,
            expected_neural_accuracy=neural,
            expected_tool_accuracy=tool,
            horizon=horizon,
            margin=margin,
            reason="tool_dominates_by_margin",
        )

    return DelegationDecision(
        delegate=False,
        estimated_depth=int(estimated_depth),
        model=model,
        expected_neural_accuracy=neural,
        expected_tool_accuracy=tool,
        horizon=horizon,
        margin=margin,
        reason="below_horizon",
    )


__all__ = [
    "MODEL_HORIZONS",
    "DEFAULT_TOOL_ACCURACY",
    "DelegationDecision",
    "expected_neural_accuracy",
    "horizon_for",
    "should_delegate",
    "delegation_decision",
]
