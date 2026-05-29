# When should my agent delegate?

> If you remember one thing from this paper: **past ~22 steps of state tracking, "think harder" is a coin flip.** Call a tool instead.

This page distils the theory into engineering rules you can implement in a single afternoon.

## The 30-second recipe

```python
from deterministic_horizon import should_delegate, delegation_decision

# In your agent's planner step:
depth = estimate_subproblem_depth(task)        # your problem-specific estimator
if should_delegate(estimated_depth=depth, model="claude-4.5-opus"):
    answer = call_tool(task)                   # BFS, search, calculator, SQL, ...
else:
    answer = call_llm(task)                    # neural chain-of-thought
```

Need the full justification (for logging or human review)?

```python
d = delegation_decision(estimated_depth=30, model="claude-4.5-opus")
print(d.explain())
# At estimated depth d=30, model 'claude-4.5-opus' is expected to reach 45% via CoT
# vs. 92% via tools (horizon d*=27). → delegate.
```

## Picking `estimated_depth`

You need an estimator. Three pragmatic options, in increasing order of fidelity:

1. **A constant per task type.** "Code search is depth ≈ 10; refactoring across 5 files is depth ≈ 40." A 30-minute lookup table beats no estimator.
2. **A planner LLM call.** Ask a small model to *count the discrete steps* needed. Don't ask "is this hard?" — ask "how many independent state changes?". The Deterministic Horizon does not apply to *that* counting prompt (it's a single-step classification).
3. **A learned estimator.** Train a tiny regressor on (task, ground-truth-depth) pairs from your traces. The paper's permutation-task instances are released as labelled data in `data/sample/`.

Get the order of magnitude right; the helper only branches at `d* ≈ 20–30`.

## Per-model horizons (PermutationProbe; Table 3 "Main results" + Table 5 "Architecture ablation")

| Model | $d^*$ | What it means for your agent |
|---|---:|---|
| `gpt-4o`          | 22 | Delegate beyond ~20-step subproblems. |
| `claude-4.5-opus` | 27 | More headroom — but still finite. |
| `o3-mini`         | 31 | Highest in our sweep ("reasoning model" — helps, but doesn't *abolish* the wall). |
| `deepseek-r1`     | 29 | Reasoning-specialised. |
| `llama-3.1-8b`    | 20 | Small open-weight — delegate aggressively. |
| `llama-3.3-70b`   | 28 | Scaling helps: +40% horizon over 8B. |
| `qwen-2.5-7b`     | 19 | Lowest in the suite. |
| `qwen-2.5-72b`    | 28 | Same $d^*$ as Llama-70B (matched $\sqrt{d_h H}$). |

These are the paper's measured 50%-accuracy crossover points for the C1 (neural CoT) condition on PermutationProbe. Only models with a paper-reported $d^*$ are listed; any other identifier (e.g. `claude-4.5-sonnet`) falls back to the cross-model `default` ($d^*=24$). The horizons generalise to other state-tracking domains (§5) with cross-task correlation $r=0.81$–$0.91$.

## When the rule does *not* apply

The Deterministic Horizon governs **deterministic state tracking** — problems where there is a single correct trajectory of intermediate states and BFS/search would solve them exactly. The helper's prediction *will* be too pessimistic on:

- **Open-ended generation** (writing, brainstorming, summarisation). No depth, no horizon.
- **Pattern-matching / retrieval tasks.** The bottleneck is the retriever, not the chain.
- **Tasks where partial credit is fine.** The horizon is calibrated to *exact* correctness; if you accept 80% on each step, the curve flattens.

For these regimes treat `should_delegate` as advisory, not prescriptive.

## Three patterns we see in production agents

1. **Planner → Router → (LLM | Tool).** Cheapest. Estimate depth in the planner, route in one line with `should_delegate`. This is the pattern most code agents converge to within a quarter of operation.
2. **Speculative dual-track.** Run both branches concurrently when latency budget allows; verify the tool result and use it as the source of truth if the two disagree. Bumps cost by ≤1.4× and absorbs estimator errors.
3. **Tool-with-fallback.** Try the tool first, fall back to neural CoT only if it errors. Strictly dominates "always LLM" when $d > d^*$ for your model.

## A worked numerical example

You're shipping a code-search agent over a 200k-LOC repo. You measure (or guess) that the average symbol-resolution chain is 14 steps on Mondays (cold cache) and 5 steps after the cache is warm.

```python
>>> from deterministic_horizon import expected_neural_accuracy, should_delegate
>>> round(expected_neural_accuracy(5, model="claude-4.5-opus"), 2)
0.91
>>> round(expected_neural_accuracy(14, model="claude-4.5-opus"), 2)
0.73
>>> should_delegate(5, model="claude-4.5-opus")    # neural ≈ tool — stay neural
False
>>> should_delegate(14, model="claude-4.5-opus")   # tool wins by > margin — delegate
True
```

So warm-cache symbol resolution stays neural, and on cold Mondays you flip to the static-analysis tool. The numbers are predictions, not guarantees — calibrate against your own eval set, and pass `margin=0.20` or `threshold=0.4` to bias the policy more towards neural.

## See also

- The decoherence model: [`theorem-cheatsheet.md`](theorem-cheatsheet.md)
- Where the constants come from: §4–§5 and Tables 3 & 5 of the [paper](../paper/ICML2026_DeterministicHorizon_CameraReady.pdf)
- The implementation: [`src/deterministic_horizon/policy.py`](../src/deterministic_horizon/policy.py)
