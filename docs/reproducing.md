# Reproducing the results

Everything in the paper reproduces from this repo. The **offline** path needs no
API keys and runs in seconds; the **full empirical** path needs model API keys.

## 1. Offline (no API keys) — seconds

```bash
pip install -e .
python examples/demo.py
```

This estimates the horizon from a synthetic decoherence simulator whose per-step
error is *exactly* the paper's $\varepsilon(d)=\varepsilon_0+\gamma d/L_{\text{eff}}$
(Theorem 4.2), and writes:

| Artefact | What it is |
|---|---|
| `analysis/figure_decay.png` | accuracy decay + fitted curve + d\* marker (the hero image) |
| `analysis/figure_conditions.png` | C1 vs C3 bar chart |
| `analysis/accuracy_by_depth.md` | per-depth accuracy table + 95% CIs |
| `analysis/horizon.json` | fitted d\*, ε₀, γ, R² |

Expected (deterministic, seed 42): **d\* ≈ 22.8**, decoherence-model fit
**R² ≈ 0.955**.

### Regenerate the committed sample artefacts

```bash
python scripts/regenerate_sample_data.py            # data/ + results/
python scripts/regenerate_sample_data.py --figures  # assets/ + analysis/ PNGs
python scripts/regenerate_sample_data.py --tables   # analysis/*.{md,json}
python scripts/regenerate_sample_data.py --all      # everything
```

…or via `make`:

```bash
make paper-figures
make paper-tables
```

## 2. Full empirical run (needs API keys)

Add keys to `.env` (see [`.env.example`](../.env.example)), then:

```bash
dh generate --task permutation --n-instances 500 --output data/perm.json
dh evaluate --model gpt-4o --instances data/perm.json \
            --conditions C1,C3 --output results/gpt4o.json
dh analyze  --results results/gpt4o.json --output analysis/gpt4o/
```

### The five conditions

| Condition | Description |
|---|---|
| **C1** | Neural chain-of-thought (standard prompting) |
| **C2** | Depth-limited CoT (oracle optimal length) |
| **C3** | Tool-integrated (BFS / verifier access) |
| **C4** | Length-encouraged prompting ("take as many steps as needed") |
| **C5** | Fine-tuned on optimal-length traces |

## 3. Scale, seeds, and cost

| Quantity | Value |
|---|---|
| Seeds | `{42, 2024, 2025}` (all results averaged over the three) |
| Full grid | 12 models × 5 conditions × 8 tasks × 500 instances × 3 seeds |
| Total evaluations | ≈ 720,000 |
| API cost | ≈ \$3,420 |
| Wall-clock (full grid, batched) | ≈ 38 h across providers' rate limits |

The headline numbers (Table 3 / Table 5):

| Metric | Value |
|---|---|
| Deterministic Horizon d\* | 19–31 steps |
| Tool-integrated accuracy (C3) | 86–94% |
| Neural CoT accuracy (C1) | 24–42% |
| Cross-model correlation r | 0.81–0.91 |
| Fine-tuning recovery (C5) | +3.2% |
| Cost efficiency (tool vs. CoT) | 4.2–4.7× |
| Decoherence-model fit | R² = 0.96 |

## 4. Determinism notes

- All generators are seeded; the offline demo is bit-for-bit reproducible.
- Real LLM calls use `temperature=0.0`, but providers do not guarantee
  determinism — expect ±1–2 points run-to-run, which is why we average over three
  seeds and report bootstrap 95% CIs ([`bootstrap_ci`](../src/metrics/statistics.py)).

Back to the [documentation hub](README.md).
