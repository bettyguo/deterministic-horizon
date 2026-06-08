<div align="center">

# 🧭 The Deterministic Horizon

### When extended chain-of-thought stops helping — and tool delegation becomes *necessary*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-46aef7.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-61%20passing-brightgreen.svg)](tests/)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bettyguo/deterministic-horizon/blob/main/notebooks/01_quickstart.ipynb)
[![Live demo](https://img.shields.io/badge/live%20demo-interactive%20explorer-8a4fff.svg)](https://bettyguo.github.io/deterministic-horizon/)

<br/>

</div>

---

## The 30-second pitch

We tested **12 frontier models** on **deterministic state-space search** — the kind of problem BFS solves in milliseconds. They all hit the same wall, at the same place:

| Model | Neural CoT (C1) | **Tool delegation (C3)** | Horizon *d*\* |
|---|---:|---:|---:|
| GPT-4o            | 28% | **90%** | 22 |
| Claude-4.5-Opus   | 35% | **94%** | 27 |
| o3-mini           | 42% | **94%** | 31 |
| DeepSeek-R1       | 40% | **93%** | 29 |

<sub>PermutationProbe, neural CoT vs. tool-integrated reasoning (paper Table&nbsp;3).</sub>

The wall sits at **d\* ∈ [19, 31] reasoning steps**. We give it a name (the **Deterministic Horizon**), derive it from the information-theoretic capacity of attention (Theorem&nbsp;4.2), and prove that **fine-tuning cannot push past it** (Theorem&nbsp;4.7).

<div align="center">
<img src="assets/figure_model_horizons.png" alt="Per-model neural CoT decay curves; each model's horizon d* falls between 19 and 31 steps, and every curve drops below the 92% tool baseline past its horizon." width="720"/>
<br/>
<sub><b>Same wall, different distances.</b> Lower baseline error and longer effective decoherence length push the horizon out — but every model crosses below the tool baseline. Regenerate with <code>dh compare-figure</code>; explore it live in the <a href="https://bettyguo.github.io/deterministic-horizon/#compare">interactive comparison</a>.</sub>
</div>

> **Why care?** Every agentic system shipping today — code agents, browser agents, planners — must decide *when to think* and *when to call a tool*. Past d\*, "think harder" is a coin flip. Hand off.

---

## Five lines that ship to your agent today

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
>>> d = delegation_decision(estimated_depth=30, model="claude-4.5-opus")
>>> d.explain()
"At estimated depth d=30, model 'claude-4.5-opus' is expected to reach 45% via CoT
 vs. 92% via tools (horizon d*=27). → delegate."
```

The decision is the paper's Theorem&nbsp;4.2 decay model, `ε(d) = ε₀ + γ·d/L_eff`, evaluated per model. Per-model horizons, when this *doesn't* apply, and three production routing patterns: **[docs/when-to-delegate.md](docs/when-to-delegate.md)**.

---

## Headline findings

| Metric | Value | Why it matters |
|---|---|---|
| Deterministic Horizon $d^*$ | **19–31 steps** | Beyond this depth, neural CoT accuracy < 50%. |
| Tool-integrated accuracy | **86–94%** | Across 8 task domains and 12 models. |
| Neural CoT accuracy | **24–42%** | The same tasks, no tools. |
| Cross-model correlation $r$ | **0.81–0.91** | Models from 6 orgs fail on the *same* instances ⇒ architectural, not training-specific. |
| Fine-tuning recovery | **+3.2%** | Theorem 4.7 predicts < 5%; the competing theory predicts > 30%. |
| Cost efficiency (tool vs. CoT) | **4.2–4.7×** | Lower cost-per-correct-solution. |
| Decoherence-model fit | **R² = 0.96** | Super-exponential decay beats linear (0.71) and exponential (0.83). |

Seeds (`{42, 2024, 2025}`), costs, and a wall-clock breakdown: **[docs/reproducing.md](docs/reproducing.md)**.

---

## The theory in three equations

**Context-dependent per-step error** (Theorem 4.2) — error grows with *position* in the chain, not just task size:

$$\varepsilon(d) = \varepsilon_0 + \gamma\,\frac{d}{L_{\text{eff}}}\qquad\Longrightarrow\qquad P(\text{correct at depth }d) \approx \exp\!\Big(-d\varepsilon_0 - \tfrac{\gamma\,d(d+1)}{2L_{\text{eff}}}\Big)$$

Here $L_{\text{eff}}$ is the **effective decoherence length** — the number of steps over which attention keeps usable state resolution, empirically $O(10^2)$ steps, *not* the raw context window $O(10^5)$ tokens.

**Attention Bottleneck** (Theorem 4.4, with a complementary achievability construction) — capacity is bounded by the architecture:

$$|\mathcal{S}_{\text{track}}| \le c(\delta,\rho_{\max})\cdot 2^{\,H\,\log_2(L/H)\,\sqrt{d_h}}$$

**Deterministic Horizon** (Theorem 4.5) — solving $P(\text{correct}) = \alpha$ gives a closed form; for GPT-4o ($\varepsilon_0=0.02,\gamma=0.15,L_{\text{eff}}=150,\alpha=0.5$) it yields $d^* \approx 22.3$:

$$d^* = \frac{-\varepsilon_0 L_{\text{eff}} + \sqrt{\varepsilon_0^2 L_{\text{eff}}^2 + 2\gamma L_{\text{eff}}\ln(1/\alpha)}}{\gamma}$$

A fourth result (Theorem 4.7) bounds fine-tuning recovery by $O(d^*/d)$ — the architectural ceiling. Proofs are in the appendix; the formulas live in [`policy.py`](src/policy.py) and [`metrics/statistics.py`](src/metrics/statistics.py).

---

## Python API

```python
from deterministic_horizon import (
    PermutationTask, generate_instances, evaluate,
    estimate_horizon, fit_decoherence_model,
    should_delegate, should_delegate_batch, delegation_decision,
    horizon_table, recommend_model,
)

# 1. Generate BFS-optimal-depth instances (depth == true BFS optimum)
task = PermutationTask(n_elements=8, seed=42)          # S_8, diameter C(8,2)=28
instances = task.generate_instances(n_instances=400, min_depth=4, max_depth=28)

# 2. Evaluate a model (needs an API key in .env)
results = evaluate(model="gpt-4o", instances=instances, conditions=["C1", "C3"])

# 3. Estimate the horizon (super-exponential fit of Theorem 4.2)
horizon = estimate_horizon(results, threshold=0.5)
print(f"d* = {horizon['d_star']:.1f}  (R² = {horizon['r_squared']:.3f})")

# 4. Route in your own agent
should_delegate(estimated_depth=horizon['d_star'] + 5, model="gpt-4o")   # → True

# 5. Plan a whole decomposition at once, or pick the right model for a depth
should_delegate_batch([5, 8, 35], model="gpt-4o")   # → [False, False, True]
recommend_model(estimated_depth=18)                  # → least over-powered model that still clears 50%
horizon_table()                                       # → per-model d* / ε₀ / L_eff rows (sorted) — the source for `dh horizons`
```

### The five experimental conditions

| Condition | Description |
|---|---|
| **C1** | Neural chain-of-thought (standard prompting) |
| **C2** | Depth-limited CoT (oracle optimal length) |
| **C3** | Tool-integrated (BFS / verifier access) |
| **C4** | Length-encouraged prompting ("take as many steps as needed") |
| **C5** | Fine-tuned on optimal-length traces |

---

## What's inside

```
deterministic-horizon/
├── src/
│   ├── policy.py        # should_delegate / delegation_decision  ← the engineering hook
│   ├── tasks/           # PermutationProbe, FSA-Sim, ArithChain (+ BFS oracle)
│   ├── models/          # Uniform interface: OpenAI / Anthropic / DeepSeek / Gemini / Together / local
│   ├── metrics/         # SSJ, SFE, super-exponential horizon fit, bootstrap CIs
│   ├── analysis.py      # Figures + tables (+ plot_model_horizons comparison)
│   ├── runners.py       # High-level evaluate(...) Python API
│   └── cli.py           # dh generate | evaluate | analyze | delegate | horizons | compare-figure
├── examples/            # demo.py (offline horizon) · agent_routing.py
├── configs/             # OmegaConf configs (model × task × experiment)
└── tests/               # pytest suite (smoke · metrics · tasks · policy · analysis)
```

