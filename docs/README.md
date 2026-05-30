# Documentation

Welcome to the documentation for **The Deterministic Horizon** — the ICML 2026
paper on when extended chain-of-thought stops helping and tool delegation
becomes *necessary*.

## Start here

| If you want to… | Read |
|---|---|
| **Route in your own agent today** | [When to delegate](when-to-delegate.md) — the `should_delegate` API, per-model horizons, three production patterns. |
| **Understand the math** | [Theorem cheat-sheet](theorem-cheatsheet.md) — every theorem in plain English, with the one-line intuition and the formula. |
| **Reproduce the numbers** | [Reproducing](reproducing.md) — seeds, costs, wall-clock, and exact commands. |
| **Quick objections answered** | [FAQ](faq.md) — "is the demo cherry-picked?", "are reasoning models useless?", and more. |
| **Play with the model live** | [Interactive horizon explorer](horizon-explorer.html) — sliders for ε₀, γ, L_eff, α; solves for d\* in real time. |
| **Run code in 60 seconds** | [Quickstart notebook](../notebooks/01_quickstart.ipynb) (Colab-friendly). |

## The one-paragraph version

Frontier LLMs fail at deterministic multi-step state tracking once the chain
exceeds a model-specific depth **d\*** — the *Deterministic Horizon*, empirically
in **[19, 31] steps**. The failure is **architectural** (causal attention cannot
keep usable state past an *effective decoherence length* L_eff ≈ O(10²) steps),
not a training preference — so fine-tuning recovers < 5%, while delegating to a
tool (BFS, a solver, SQL, a verifier) recovers 50–70 points. The engineering
takeaway: **estimate the depth of your subproblem; past d\*, hand off.**

## Map of the codebase

```
src/
├── policy.py        should_delegate / delegation_decision   ← the engineering hook
├── tasks/           PermutationProbe · FSA-Sim · ArithChain (+ BFS oracle)
├── models/          OpenAI / Anthropic / DeepSeek / local adapters
├── metrics/         SSJ · SFE · super-exponential horizon fit · bootstrap CIs
├── analysis.py      figure + table generation
├── runners.py       high-level evaluate(...) API
└── cli.py           dh generate | evaluate | analyze
```

See the repository [README](../README.md) for installation and the 30-second pitch.
