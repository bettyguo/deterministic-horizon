#!/usr/bin/env python
"""
Regenerate the committed sample artifacts so they are fully consistent with the
paper's PermutationProbe definition and decoherence model.

Outputs (deterministic given the seed):
  * data/sample/permutation_n8.json     — BFS-optimal-depth instances on S_8
  * results/sample/synthetic_results.json — C1 (neural CoT) vs C3 (BFS tool)

The neural-CoT correctness is sampled from the paper-canonical per-step error
ε(i) = ε₀ + γ·i/L_eff (Theorem 4.2; ε₀=0.02, γ=0.15, L_eff=150), which places
the Deterministic Horizon at d* ≈ 22. The BFS tool is exact, so C3 is always
correct. All instances have ``optimal_depth`` equal to their true BFS-optimal
depth (= inversion count under adjacent transpositions), so no instance exceeds
the S_8 diameter of 28.

Usage:
    python scripts/regenerate_sample_data.py            # data + results (default)
    python scripts/regenerate_sample_data.py --figures  # + assets/ & analysis/ PNGs
    python scripts/regenerate_sample_data.py --tables   # + analysis/*.{md,json}
    python scripts/regenerate_sample_data.py --all      # everything
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from deterministic_horizon import PermutationTask

SEED = 42
N_ELEMENTS = 8
DEPTHS = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]  # all <= C(8,2) = 28
INSTANCES_PER_DEPTH = 150       # drives the decoherence-model fit (results file)
INSTANCES_PER_DEPTH_ONDISK = 6  # full instances kept in the data file (subset)

# Paper-canonical decoherence constants (Theorem 4.2 / §4).
EPS0 = 0.02
GAMMA = 0.15
L_EFF = 150

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample" / "permutation_n8.json"
RESULTS_PATH = ROOT / "results" / "sample" / "synthetic_results.json"


def ssj_precision_recall(depth: int) -> tuple[float, float, float]:
    """
    State-Space Jaccard with precision/recall at ``depth``, following the
    paper's measured super-exponential decay (Table 4 / Fig. SSJ-decay). Both
    precision and recall decay together — the signature of *capability* failure
    (Decoherence), not *preference* failure (Simplicity Bias).
    """
    d = float(depth)
    ssj = 0.95 * math.exp(-0.0196 * d - 0.00087 * d * d)
    precision = math.exp(-0.009 * d - 0.00075 * d * d)
    recall = math.exp(-0.013 * d - 0.00085 * d * d)
    return round(ssj, 4), round(precision, 4), round(recall, 4)


def simulate_neural_cot(task: PermutationTask, instance, rng: random.Random) -> bool:
    """Absorbing-error neural CoT: corrupt step i w.p. ε(i)=ε₀+γ·i/L_eff."""
    state = list(instance.initial_state)
    for step, optimal_op in enumerate(instance.optimal_solution):
        eps = min(EPS0 + GAMMA * step / L_EFF, 0.95)
        if rng.random() < eps:
            op = rng.choice([o for o in task.operators if o != optimal_op])
        else:
            op = optimal_op
        state = task.apply_operator(state, op)
    return task.state_equal(state, instance.target_state)


def regenerate_data() -> list[dict]:
    """Write data/sample + results/sample and return the results list."""
    task = PermutationTask(seed=SEED, n_elements=N_ELEMENTS)
    sim_rng = random.Random(SEED)

    results = []
    ondisk_instances = []
    for depth in DEPTHS:
        for k in range(INSTANCES_PER_DEPTH):
            inst = task.generate_instance(target_depth=depth)
            if k < INSTANCES_PER_DEPTH_ONDISK:
                ondisk_instances.append(inst)
            cot_correct = simulate_neural_cot(task, inst, sim_rng)
            ssj, precision, recall = ssj_precision_recall(inst.optimal_depth)
            results.append(
                {
                    "instance_id": inst.instance_id,
                    "condition": "C1",
                    "model": "synthetic-noisy-cot",
                    "optimal_depth": inst.optimal_depth,
                    "correct": cot_correct,
                    "ssj_score": ssj,
                    "precision": precision,
                    "recall": recall,
                }
            )
            results.append(
                {
                    "instance_id": inst.instance_id,
                    "condition": "C3",
                    "model": "bfs-tool",
                    "optimal_depth": inst.optimal_depth,
                    "correct": True,  # exact BFS solver
                }
            )

    instances = ondisk_instances
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(
        json.dumps([i.to_dict() for i in instances], indent=2), encoding="utf-8"
    )
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

    c1 = [r for r in results if r["condition"] == "C1"]
    acc = sum(r["correct"] for r in c1) / len(c1)
    print(f"Wrote {len(instances)} instances -> {DATA_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(results)} results   -> {RESULTS_PATH.relative_to(ROOT)}")
    print(f"Overall C1 accuracy: {acc:.1%} (depths {DEPTHS})")
    return results


def _load_results() -> list[dict]:
    if RESULTS_PATH.exists():
        return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    return regenerate_data()


def regenerate_figures(results: list[dict] | None = None) -> None:
    """Regenerate the paper figures into assets/ (hero images) and analysis/."""
    from deterministic_horizon import generate_figures

    results = results if results is not None else _load_results()
    for out_dir in ("assets", "analysis"):
        paths = generate_figures(results, output_dir=ROOT / out_dir, dpi=200)
        for p in paths:
            print(f"Wrote figure -> {Path(p).relative_to(ROOT)}")


def regenerate_tables(results: list[dict] | None = None) -> None:
    """Regenerate analysis/*.{md,json} (accuracy-by-depth, conditions, horizon)."""
    from deterministic_horizon import generate_tables

    results = results if results is not None else _load_results()
    paths = generate_tables(results, output_dir=ROOT / "analysis")
    for p in paths.values():
        print(f"Wrote table -> {Path(p).relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures", action="store_true", help="Regenerate PNG figures.")
    parser.add_argument("--tables", action="store_true", help="Regenerate md/json tables.")
    parser.add_argument("--all", action="store_true", help="Data + figures + tables.")
    args = parser.parse_args(argv)

    # Default (no flags) reproduces the original behaviour: data + results only.
    only_artifacts = (args.figures or args.tables) and not args.all
    results = None
    if args.all or not only_artifacts:
        results = regenerate_data()
    if args.figures or args.all:
        regenerate_figures(results)
    if args.tables or args.all:
        regenerate_tables(results)


if __name__ == "__main__":
    main()
