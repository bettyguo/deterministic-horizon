# Architecture

The codebase is intentionally small (~3.5k LOC) so contributors can read it in an afternoon. Here's the map.

```
src/deterministic_horizon/
├── __init__.py        # Public API surface (lazy-imports model adapters)
├── policy.py          # Decision helper: should_delegate / delegation_decision
├── runners.py         # High-level evaluate(model, instances, conditions)
├── analysis.py        # Figure + table generation from result JSON
├── cli.py             # `dh generate | evaluate | analyze | train`
├── config.py          # OmegaConf loader for configs/*
├── tasks/
│   ├── base.py        # BaseTask, TaskInstance, TaskResult
│   ├── permutation.py # PermutationProbe (adjacent-transposition puzzle on S_n)
│   ├── fsa.py         # Finite-state-automaton simulation
│   └── arithmetic.py  # Multi-step arithmetic chains
├── models/
│   ├── base.py            # BaseModel, ModelResponse
│   ├── openai_models.py   # OpenAI chat-completion adapter
│   ├── anthropic_models.py# Anthropic messages adapter
│   ├── deepseek_models.py # DeepSeek adapter
│   └── local_models.py    # HuggingFace transformers adapter
├── metrics/
│   ├── ssj.py        # State-Space Jaccard (capability vs. preference failure)
│   ├── sfe.py        # Step-to-First-Error
│   └── statistics.py # estimate_horizon, fit_decoherence_model, bootstrap_ci, ...
└── training/
    └── finetune.py   # Reference fine-tuning loop for the C5 condition
```

## Where to plug in

| You want to add… | Implement | Reference |
|---|---|---|
| **A new task** | `BaseTask` subclass with 5 methods | [`tasks/permutation.py`](../src/deterministic_horizon/tasks/permutation.py) |
| **A new model adapter** | `BaseModel` subclass + entry in `MODEL_REGISTRY` | [`models/openai_models.py`](../src/deterministic_horizon/models/openai_models.py) |
| **A new metric** | A free function in `metrics/` re-exported from `metrics/__init__.py` | [`metrics/ssj.py`](../src/deterministic_horizon/metrics/ssj.py) |
| **A new figure** | A `_plot_*` private function in `analysis.py` registered from `generate_figures` | [`analysis.py`](../src/deterministic_horizon/analysis.py) |

## Design principles

1. **Optional dependencies stay optional.** `import deterministic_horizon` must work without `openai`, `anthropic`, `torch`. Model adapters use lazy imports.
2. **Tasks always have a BFS oracle.** Without it, you can't define "optimal depth" — and without that, you can't fit a horizon. Every `BaseTask` must implement `bfs_solve`.
3. **Reproducible by default.** Every random op takes a seed; we pin `{42, 2024, 2025}` for the paper.
4. **Failures don't poison the run.** `runners.run_evaluation` catches per-instance exceptions and records them as failed results rather than aborting.

## Data flow

```
configs/*.yaml ──► generate_instances(...) ──► data/*.json
                                                     │
                                                     ▼
                          dh evaluate ─► run_evaluation ─► results/*.json
                                                                  │
                                                                  ▼
                                          dh analyze ─► analysis/*.{png,md,json}
```

Each stage is independently runnable: drop in your own instances JSON, your own results JSON, or your own analysis script.
