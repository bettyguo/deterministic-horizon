# FAQ

## Is the offline demo cherry-picked?

No. The demo uses a *synthetic* reasoner whose per-step error follows the context-dependent model from Theorem 1. It's a controlled illustration of the prediction — the cross-model empirical numbers come from real API calls (12 models × 5 conditions × 8 tasks × 500 instances × 3 seeds = 720,000 evaluations, $3,420 in API cost).

## How is this different from "transformers can't do X" papers?

Prior expressivity work (Merrill 2024, Hahn 2020, Peng et al. 2024) proves what transformers *cannot compute in principle* — asymptotic statements about $\text{TC}^0$ or the like. We show what frontier models *cannot reliably execute in practice* at the depths real systems actually run at, give a closed-form bound, and prove fine-tuning cannot push past it. The Deterministic Horizon is a usable engineering quantity (~22 steps), not just an asymptotic.

## Does this mean reasoning models are useless?

The opposite — the paper tells you exactly *when* to use them and *when* to delegate. Past $d^\star$, neural CoT is a coin flip and tools win by 50–70 percentage points. Many real workloads have depth $< d^\star$ and benefit from extended reasoning. The point is to know the boundary.

## Why permutation puzzles?

Three reasons: they have an unambiguous BFS oracle (we always know the optimal depth), they cleanly separate *capability* from *preference* failure modes (the SSJ metric needs canonical intermediate states), and they're small enough to test at scale cheaply. The cross-task correlation analysis in §5 ($r = 0.81$–$0.91$ across permutation, FSA, and arithmetic) shows the conclusions are not artefacts of the toy domain.

## Does this apply to Mixture-of-Experts / Mamba / RWKV?

The decoherence bound is derived for decoder-only causal attention. State-space models (SSMs) share the $\text{TC}^0$ ceiling (Merrill 2024 — "the illusion of state") but the per-step capacity term differs, so the same $d^*$ values need not transfer. Extending the framework to MoE / Mamba / RWKV is open future work (see the research issue drafts under `.github/ISSUE_DRAFTS/`), and contributions are welcome.

## I want to try this on my own task. Where do I start?

Subclass `deterministic_horizon.tasks.BaseTask` and implement five methods (`initial_state`, `apply_operator`, `state_equal`, `state_to_string`, `parse_state`). That's enough to run all five conditions. See [`tasks/permutation.py`](../src/deterministic_horizon/tasks/permutation.py) for the reference implementation. Then either run the CLI or call `dh.evaluate(...)`.

## Do I need GPUs?

For reproducing the cached numbers — no. For live API-driven evaluations — no. For the fine-tuning experiment (C5) — yes, a single A100 is enough. For local open-weight evaluations (Llama, Qwen) — yes, but we expose a `vLLM` backend that runs comfortably on 1–4× A100.

## What's the practitioner takeaway in one sentence?

When the next subproblem your agent faces is $\gtrsim 22$ deterministic state-tracking steps, route to a tool. Use [`should_delegate()`](when-to-delegate.md) to pick the threshold for your specific model.

## How do I cite this?

```bibtex
@inproceedings{guo2026deterministic,
  title        = {The Deterministic Horizon: When Extended Reasoning Fails
                  and Tool Delegation Becomes Necessary},
  author       = {Guo, Dongxin and Wu, Jikun and Yiu, Siu Ming},
  booktitle    = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year         = {2026},
}
```

The repo also ships a `CITATION.cff` so the GitHub "Cite this repository" button works.
