# Reproducing the paper

## TL;DR

```bash
git clone https://github.com/bettyguo/deterministic-horizon
cd deterministic-horizon
pip install -e ".[dev,all]"
make paper-figures
make paper-tables
```

This regenerates every figure and table in the paper from the **cached, pre-computed results** in `results/sample/`. No API keys needed; takes ~10 seconds.

## Live reproduction (with API keys)

```bash
# 1) Generate instances (deterministic; same as paper)
# For n=8 the BFS-optimal depth is capped at the diameter C(8,2)=28; use a
# larger n for deeper instances (the paper uses n in {8, 12, 16}).
dh generate --task permutation --n-instances 500 \
            --min-depth 4 --max-depth 28 --seed 42 \
            --output data/permutation_n8.json

# 2) Evaluate one or more models
dh evaluate --model gpt-4o --instances data/permutation_n8.json \
            --conditions C1,C2,C3,C4 --output results/gpt4o.json
dh evaluate --model claude-4.5-sonnet --instances data/permutation_n8.json \
            --conditions C1,C2,C3,C4 --output results/claude.json

# 3) Aggregate into figures + tables
dh analyze --results results/gpt4o.json --output analysis/gpt4o/
dh analyze --results results/claude.json --output analysis/claude/
```

## Seeds and instances

| Seed | Used for |
|---:|---|
| 42  | Main results (Figures 2, 3, 5; Tables 2, 3) |
| 2024 | Replication seed (Appendix B) |
| 2025 | Replication seed (Appendix B) |

The paper reports means over the three seeds with bootstrap 95% CIs.

## Hardware

The numbers in the paper were collected on consumer hardware (M3 Mac and a single A100 for the local-model evaluations) plus API access. Wall-clock breakdown:

| Stage | Time | Cost |
|---|---|---|
| Instance generation (BFS-optimal, up to depth 60 at n=16) | ~30 minutes (single core) | — |
| API evaluations (12 models × 5 conditions × 8 tasks × 500 instances × 3 seeds) | ~36 hours wall-clock | ~$3,420 |
| Fine-tuning experiment (C5) | ~6 hours on 1× A100 | ~$15 |
| Analysis + figures | ~2 minutes | — |

## What you should see

After `make paper-figures` you should have:

- `assets/figure_decay.png` — accuracy decay with horizon marked.
- `assets/figure_conditions.png` — C1 / C3 bar comparison.
- `assets/figure_ssj.png` — SSJ precision/recall split.

And under `analysis/` after `make paper-tables`:

- `analysis/accuracy_by_depth.md`
- `analysis/conditions.md`
- `analysis/horizon.json`

Quick sanity check: the JSON should show `d_star` somewhere in the range [19, 31] and `r_squared` ≥ 0.95.

## If a number doesn't match

1. Run `pytest -q` — if these fail, your environment is broken, not the paper.
2. Check `pip freeze | grep -E "numpy|scipy|matplotlib"`; we use `numpy>=1.24, scipy>=1.10`.
3. Compare against `results/sample/synthetic_results.json` byte-for-byte — these are committed and never change.
4. Still off? Open an issue with the offending number, your platform, and the seed.
