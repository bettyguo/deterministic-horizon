#!/usr/bin/env python
"""
60-second offline demo of the Deterministic Horizon.

Run this script without any API keys — it reproduces the headline finding
from the paper using a *synthetic* noisy reasoner whose per-step error
follows the context-dependent model ε(d) = ε₀ + γ·d/L_eff (Theorem 4.2).
Tool-integrated reasoning is simulated by running an exact BFS solver.

What you should see:
    • Neural CoT accuracy crosses 50% at the Deterministic Horizon d* ≈ 22.
    • BFS-as-a-tool stays at ~100% regardless of depth.
    • The empirical decay curve matches Theorem 4.2 with R² ≳ 0.95.
    • A figure is written to ``analysis/figure_decay.png``.

Usage:
    python examples/demo.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from deterministic_horizon import PermutationTask
from deterministic_horizon.analysis import generate_figures, generate_tables
from deterministic_horizon.metrics import estimate_horizon

# ---------- Configuration ----------
SEED = 42
N_ELEMENTS = 8  # S_8, adjacent-transposition diameter C(8,2) = 28
DEPTHS = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]  # all <= diameter
INSTANCES_PER_DEPTH = 80

# Paper-canonical decoherence constants (Theorem 4.2 / §4 numerical example):
# ε(d) = ε₀ + γ·d/L_eff, which places the GPT-4o horizon at d* ≈ 22.3.
# L_eff is the *effective* decoherence length (O(10²) steps), NOT the raw
# context window — using the raw context window would erase the quadratic term.
EPS0 = 0.02          # baseline per-step error
GAMMA = 0.15         # attention decay rate
L_EFF = 150          # effective decoherence length


def simulate_neural_cot(task: PermutationTask, instance, rng: random.Random) -> bool:
    """
    Simulate a neural CoT reasoner with context-dependent per-step error
    ε(i) = ε₀ + γ·i/L_eff (Theorem 4.2 of the paper). At step i we corrupt the
    optimal operator with probability ε(i); otherwise we follow it. The
    trace is then evaluated against the ground-truth target state.

    Aggregating across many instances yields the super-exponential decay
    P(correct at depth d) ≈ exp(-d·ε₀ − γ·d(d+1)/(2·L_eff)).
    """
    state = list(instance.initial_state)
    for step, optimal_op in enumerate(instance.optimal_solution):
        eps = min(EPS0 + GAMMA * step / L_EFF, 0.95)
        if rng.random() < eps:
            op = rng.choice([o for o in task.operators if o != optimal_op])
        else:
            op = optimal_op
        state = task.apply_operator(state, op)

    return task.state_equal(state, instance.target_state)


def simulate_tool(task: PermutationTask, instance) -> bool:
    """
    Tool-integrated solver (C3): an exact BFS solver always returns the optimal
    path. Each instance ships with its verified BFS-optimal solution, so we
    replay it (cheap, O(depth)) rather than re-running BFS on every call.
    """
    state = list(instance.initial_state)
    for op in instance.optimal_solution:
        state = task.apply_operator(state, op)
    return task.state_equal(state, instance.target_state)


def main() -> None:
    rng = random.Random(SEED)
    task = PermutationTask(seed=SEED, n_elements=N_ELEMENTS)

    print("=" * 72)
    print("Deterministic Horizon — offline demo (no API keys)")
    print("=" * 72)
    print(f"Permutation puzzles, n={N_ELEMENTS} elements, {INSTANCES_PER_DEPTH} per depth")
    print(f"Depths tested: {DEPTHS}\n")

    results: list[dict] = []
    print(f"{'depth':>5}  {'neural CoT':>12}  {'tool (BFS)':>12}")
    print(f"{'-----':>5}  {'-' * 12}  {'-' * 12}")

    for depth in DEPTHS:
        cot_hits = 0
        tool_hits = 0
        for _ in range(INSTANCES_PER_DEPTH):
            inst = task.generate_instance(target_depth=depth)
            cot_correct = simulate_neural_cot(task, inst, rng)
            tool_correct = simulate_tool(task, inst)
            cot_hits += int(cot_correct)
            tool_hits += int(tool_correct)
            results.append(
                {
                    "instance_id": inst.instance_id,
                    "condition": "C1",
                    "model": "synthetic-noisy-cot",
                    "optimal_depth": depth,
                    "correct": cot_correct,
                }
            )
            results.append(
                {
                    "instance_id": inst.instance_id,
                    "condition": "C3",
                    "model": "bfs-tool",
                    "optimal_depth": depth,
                    "correct": tool_correct,
                }
            )
        cot_pct = 100 * cot_hits / INSTANCES_PER_DEPTH
        tool_pct = 100 * tool_hits / INSTANCES_PER_DEPTH
        print(f"{depth:>5}  {cot_pct:>11.1f}%  {tool_pct:>11.1f}%")

    # --- Horizon fit (use the neural CoT condition only) ---
    cot_results = [r for r in results if r["condition"] == "C1"]
    horizon = estimate_horizon(cot_results, threshold=0.5)
    print()
    print("Deterministic Horizon (50% threshold):")
    print(f"  d* = {horizon['d_star']:.1f}  "
          f"(95% CI [{horizon.get('d_star_ci_low', math.nan):.1f}, "
          f"{horizon.get('d_star_ci_high', math.nan):.1f}])")
    if "r_squared" in horizon:
        print(f"  decoherence-model fit R² = {horizon['r_squared']:.3f}")

    # --- Write outputs ---
    out = Path("analysis")
    out.mkdir(parents=True, exist_ok=True)
    figs = generate_figures(results, output_dir=out, title="Demo: synthetic CoT vs. BFS tool")
    tables = generate_tables(results, output_dir=out)

    print()
    print("Saved artefacts:")
    for f in figs:
        print(f"  · {f}")
    for name, p in tables.items():
        print(f"  · {p}  ({name})")

    print("\n✓ Demo complete. Open analysis/figure_decay.png to see the decoherence curve.")


if __name__ == "__main__":
    main()
