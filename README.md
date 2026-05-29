<div align="center">

# The Deterministic Horizon

**When extended chain-of-thought stops helping — and tool delegation becomes the only way forward.**

[![Paper](https://img.shields.io/badge/paper-ICML%202026-b31b1b.svg)](paper/ICML2026_DeterministicHorizon_FINAL.pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%E2%80%933.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-46aef7.svg)](https://github.com/astral-sh/ruff)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/deterministic-horizon/deterministic-horizon/blob/main/notebooks/01_quickstart.ipynb)

</div>


## The 30-second pitch

We tested **12 frontier models** on **state-space search** (the kind of problem BFS solves in milliseconds) — they all collapse at the same wall:

|  | Neural CoT (C1) | **Tool delegation (C3)** |
|---|---:|---:|
| GPT-4o | 28% | **90%** |
| Claude 4.5 Opus | 35% | **94%** |
| o3-mini | 42% | **94%** |
| DeepSeek-R1 | 40% | **93%** |

The wall is at **d\* ∈ [19, 31]** reasoning steps. We give the wall a name (the **Deterministic Horizon**), derive it from attention information theory (Theorem 1), and prove fine-tuning *cannot* push past it (Theorem 4).

> **Why care?** Every agentic system shipping today — code agents, browsers, planners — has to decide *when* to think and *when* to call a tool. Past d\*, "think harder" doesn't help. Hand off.

---

## Five lines of code that ship to your agent today

```python
from deterministic_horizon import should_delegate

# In your planner loop:
if should_delegate(estimated_depth=subproblem_depth, model="claude-4.5-opus"):
    answer = call_tool(subproblem)        # BFS / search / SQL / verifier
else:
    answer = call_llm(subproblem)         # neural chain-of-thought
```

Need the full justification (for logging or eval)?

```python
>>> from deterministic_horizon import delegation_decision
>>> d = delegation_decision(estimated_depth=27, model="claude-4.5-opus")
>>> d.explain()
"At estimated depth d=27, model 'claude-4.5-opus' is expected to reach 31% via CoT
 vs. 92% via tools (horizon d*=28). → delegate."
```

Per-model horizons, when this *doesn't* apply, and three production routing patterns: [docs/when-to-delegate.md](docs/when-to-delegate.md).

---

## 60-second offline demo (no API keys)

```bash
git clone https://github.com/deterministic-horizon/deterministic-horizon
cd deterministic-horizon
pip install -e .
python examples/demo.py            # offline horizon estimation
python examples/agent_routing.py   # routing pattern, end-to-end
```

You'll see the **horizon estimated live** from a synthetic decoherence simulator, decoherence-model fit R² ≈ 0.97, and a publication-grade figure saved to `analysis/figure_decay.png` (matches the hero image).

Want the **real LLMs**? Add API keys to `.env` (see `.env.example`) and:

```bash
dh evaluate --model gpt-4o --instances data/sample/permutation_n8.json \
            --conditions C1,C3 --output results/gpt4o.json
dh analyze  --results results/gpt4o.json --output analysis/gpt4o/
```

---

## Headline findings (replicating the paper)

| Metric | Value | Why it matters |
|---|---|---|
| Deterministic Horizon $d^*$ | **19–31 steps** | Beyond this depth, neural CoT accuracy < 50% |
| Tool-integrated accuracy | **86–94%** | Across 8 task domains, 12 models |
| Cross-model correlation $r$ | **0.81–0.91** | Failure is *architectural*, not training-specific |
| Fine-tuning recovery | **+3.2%** | Predicted < 5% by Theorem 4 (vs > 30% by competing theory) |
| Decoherence-model fit | **R² = 0.96** | Super-exponential decay matches data |

Full reproduction:

```bash
make paper-figures   # rebuilds every figure in the paper
make paper-tables    # rebuilds every table
```

See [docs/reproducing.md](docs/reproducing.md) for seeds, costs, and a wall-clock breakdown.

---

## What's inside

```
deterministic-horizon/
├── src/deterministic_horizon/
│   ├── policy.py       # should_delegate / delegation_decision (THE engineering hook)
│   ├── tasks/          # PermutationProbe, FSA-Sim, ArithChain (+ BFS oracles)
│   ├── models/         # Uniform interface: OpenAI / Anthropic / DeepSeek / local
│   ├── metrics/        # SSJ, SFE, super-exponential horizon fit, bootstrap CIs
│   ├── analysis.py     # Figure + table generation
│   ├── runners.py      # High-level `evaluate(...)` Python API
│   └── cli.py          # `dh generate | evaluate | analyze`
├── examples/
│   ├── demo.py            # Offline reproduction of d*
│   └── agent_routing.py   # Production routing pattern using should_delegate
├── notebooks/
│   └── 01_quickstart.ipynb   # 60-second Colab-friendly walkthrough
├── docs/                  # When-to-delegate · Theorem cheatsheet · FAQ · Reproducing
├── data/sample/           # Pre-generated permutation instances
├── results/sample/        # Pre-computed synthetic results
├── configs/               # OmegaConf configs (model × task × experiment)
├── paper/                 # ICML 2026 LaTeX + final PDF
└── tests/                 # pytest suite (smoke / metrics / tasks / policy / analysis)
```

---

## Why this is different from "overthinking" papers

| | Simplicity Bias (prior work) | **Decoherence (this work)** |
|---|---|---|
| Cause | Training preference for short outputs | Information-theoretic capacity bound |
| Fix | Fine-tune on long traces | **No fix** — it's architectural |
| Predicted fine-tune gain | > 30% | **< 5%**  ← we observe 3.2% ✅ |
| Predicted prompt-length gain | > 10% | **< 2%**  ← we observe 1.1% ✅ |
| Predicted cross-model $r$ | Low | **High**  ← we observe 0.86 ✅ |
| Enc-dec advantage | None | **2–3×** ← we observe 2.8× ✅ |

Four divergent predictions, four wins. See §1 of the paper or [docs/theorem-cheatsheet.md](docs/theorem-cheatsheet.md).

---

## The core theorem (in one line)

The number of distinct states a decoder-only transformer can reliably track is

$$|\mathcal{S}_{\text{track}}| \;\leq\; c(\delta, \rho_{\max}) \cdot 2^{H \cdot \log_2(L/H) \cdot \sqrt{d_h}}$$

with **matching lower bound** (Theorem 2). Per-step error is context-dependent
$\varepsilon(d) = \varepsilon_0 + \gamma\, d/L$ (Theorem 1, derived from attention entropy),
yielding the closed-form Deterministic Horizon

$$d^\star \;\approx\; \frac{1}{\gamma}\Bigl(\sqrt{2 L \ln(1/\alpha)} \;-\; \varepsilon_0\, L\Bigr)$$

and the fine-tuning ceiling $\text{Acc}_{\text{fine-tune}} \leq \text{Acc}_{\text{baseline}} + O(d^\star/d)$.
Proofs in the appendix; ablations in §6. Plain-English version: [docs/theorem-cheatsheet.md](docs/theorem-cheatsheet.md).

---

## Python API

```python
from deterministic_horizon import (
    PermutationTask, generate_instances, evaluate,
    estimate_horizon, fit_decoherence_model,
    should_delegate, delegation_decision,
)

# 1. Generate task instances
task = PermutationTask(n_elements=8, seed=42)
instances = task.generate_instances(n_instances=400, min_depth=4, max_depth=40)

# 2. Evaluate a model (requires an API key in .env)
results = evaluate(model="gpt-4o", instances=instances, conditions=["C1", "C3"])

# 3. Estimate the horizon
horizon = estimate_horizon(results, threshold=0.5)
print(f"d* = {horizon['d_star']:.1f}  (R² = {horizon['r_squared']:.3f})")

# 4. Use it in your own agent's routing decision
should_delegate(estimated_depth=horizon['d_star'] + 5, model="gpt-4o")  # → True
```

### Conditions

| Condition | Description |
|---|---|
| **C1** | Neural chain-of-thought (standard prompting) |
| **C2** | Direct answer, no reasoning |
| **C3** | Tool-integrated (BFS / verifier access) |
| **C4** | Length-encouraged prompting ("take as many steps as needed") |
| **C5** | Fine-tuned on optimal-length traces |

---

## Installation

```bash
# Slim install (core metrics + analysis, no LLM clients)
pip install -e .

# With OpenAI + Anthropic clients
pip install -e ".[openai,anthropic]"

# With local model support (PyTorch / transformers)
pip install -e ".[local]"

# Everything
pip install -e ".[all,dev]"
```

Requires Python 3.10–3.12. Tested on Linux, macOS, and Windows via [CI](.github/workflows/ci.yml).

---

## FAQ (highlights)

<details>
<summary><b>Is the demo cherry-picked?</b></summary>

No. The demo uses a *synthetic* reasoner whose per-step error follows the exact context-dependent model from the paper (Theorem 1). The cross-model empirical numbers in `results/paper/` come from real API calls — 12 models × 5 conditions × 8 tasks × 500 instances × 3 seeds = 720,000 evaluations, $3,420 in API cost.
</details>

<details>
<summary><b>How is this different from "transformers can't do X" papers?</b></summary>

Prior expressivity work proves what transformers *cannot compute in principle*. We show what frontier models *cannot reliably execute in practice*, give a closed-form bound on the wall, and prove fine-tuning cannot move it. The Deterministic Horizon is a usable engineering quantity, not an asymptotic.
</details>

<details>
<summary><b>Does this mean reasoning models are useless?</b></summary>

Opposite — it tells you exactly *when* to use them and *when* to delegate. Past $d^*$, neural CoT is a coin flip; tools win by 50–70 percentage points.
</details>

Full FAQ: [docs/faq.md](docs/faq.md).

---

## Citation

If you use this code or build on the ideas, please cite:

```bibtex
@inproceedings{guo2026deterministic,
  author = {Guo, Dongxin and Wu, Jikun and Yiu, Siu-Ming},
  title = {The Deterministic Horizon: When Extended Reasoning Fails and Tool Delegation Becomes Necessary},
  booktitle = {Forty-third International Conference on Machine Learning, {ICML} 2026, Seoul, South Korea, July 6-11, 2026},
  series = {Proceedings of Machine Learning Research},
  publisher = {{PMLR} / OpenReview.net},
  year = {2026}
}
```

A `CITATION.cff` is included so GitHub will auto-populate the "Cite this repository" button.

---

## Contributing

Bug reports, new tasks, and extensions welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md); issue templates and a PR checklist are wired up via [`.github/`](.github/). Open issues tagged `good-first-issue` are great starting points.

**Roadmap** (help wanted):

- [ ] SWE-Bench-State integration
- [ ] WebArena-Nav adapter
- [ ] Mamba / RWKV decoherence study
- [ ] Interactive horizon visualiser (web)
- [ ] Hugging Face Spaces demo

---

<div align="center">

**Found this useful?** Star the repo and share with anyone shipping agentic systems.
The Deterministic Horizon isn't a soft suggestion — it's a wall.

[Paper](paper/ICML2026_DeterministicHorizon_FINAL.pdf) · [Docs](docs/README.md) · [When to delegate](docs/when-to-delegate.md) · [Quickstart notebook](notebooks/01_quickstart.ipynb) · [Issues](https://github.com/deterministic-horizon/deterministic-horizon/issues)

</div>
