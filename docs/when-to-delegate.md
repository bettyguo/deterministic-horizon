# When to delegate

This is the engineering core of the paper, distilled into one decision:

> **At this subproblem's estimated depth, should my agent think harder (neural
> chain-of-thought) or call a tool (BFS / solver / SQL / verifier)?**

The answer is a single function call.

```python
from deterministic_horizon import should_delegate

if should_delegate(estimated_depth=subproblem_depth, model="claude-4.5-opus"):
    answer = call_tool(subproblem)     # past the horizon — neural CoT is a coin flip
else:
    answer = call_llm(subproblem)      # below the horizon — reasoning is reliable
```

## The decision, explained

`should_delegate` is a thin boolean over `delegation_decision`, which returns the
full justification. They **always agree**.

```python
>>> from deterministic_horizon import delegation_decision
>>> d = delegation_decision(estimated_depth=30, model="claude-4.5-opus")
>>> d.explain()
"At estimated depth d=30, model 'claude-4.5-opus' is expected to reach 45% via CoT
 vs. 92% via tools (horizon d*=27). → delegate."
>>> d.delegate, round(d.expected_neural_accuracy, 2), d.reason
(True, 0.45, 'above_horizon')
```

A tool is recommended when **either** condition holds (and a tool is available):

1. **Below threshold** — expected neural accuracy `< threshold` (default 0.5).
   You're past d\*; thinking harder is a coin flip.
2. **Tool dominates by margin** — even above threshold, the tool beats neural
   reasoning by more than `margin` (default 0.10). Don't burn tokens to break even.

The expected neural accuracy is the paper's closed-form decay (Theorem 4.2):

```
P(correct at depth d) ≈ exp( −d·ε₀ − γ·d(d+1) / (2·L_eff) )
```

evaluated with each model's calibrated `(ε₀, L_eff)`. See the
[theorem cheat-sheet](theorem-cheatsheet.md) for where this comes from.

## Per-model horizons

`d*` is the depth at which expected neural accuracy crosses 0.5. These are the
paper's measured values on PermutationProbe (Table 3 / Table 5):

| Model | d\* | ε₀ | Notes |
|---|---:|---:|---|
| `qwen-2.5-7b`    | 19 | 0.023 | smallest horizon in the suite |
| `llama-3.1-8b`   | 20 | 0.022 | |
| `gpt-4o`         | 22 | 0.020 | **paper-canonical** (ε₀=0.02, L_eff=150, d\*≈22.3) |
| `default`        | 24 | 0.020 | unknown models → midpoint of [19, 31] |
| `claude-4.5-opus`| 27 | 0.018 | |
| `llama-3.3-70b`  | 28 | 0.018 | |
| `qwen-2.5-72b`   | 28 | 0.018 | |
| `deepseek-r1`    | 29 | 0.015 | reasoning-specialised |
| `o3-mini`        | 31 | 0.014 | highest horizon in the suite |

```python
from deterministic_horizon import horizon_for, expected_neural_accuracy

horizon_for("o3-mini")                       # 31.0
expected_neural_accuracy(15, "gpt-4o")       # ~0.62  (below d* → reason)
expected_neural_accuracy(30, "gpt-4o")       # ~0.20  (past d* → delegate)
```

Unknown identifiers fall back to `"default"`. You can also override the
decoherence parameters directly if you've calibrated your own:

```python
expected_neural_accuracy(20, eps0=0.02, l_eff=150)
```

## Three production routing patterns

### 1. Depth-gated planner

Estimate depth once per subproblem; route on the boolean. This is the five-line
example above. Use it when you already have a depth estimate (a planner's plan
length, a parse tree depth, a known recursion bound).

### 2. Confidence-margin routing

Pass your tool's *measured* accuracy so the margin rule reflects reality:

```python
should_delegate(estimated_depth=d, model=m, tool_accuracy=0.88, margin=0.10)
```

If your verifier is only 80% reliable, the function won't over-delegate to it.

### 3. Graceful degradation when no tool exists

```python
d = delegation_decision(estimated_depth=40, model="gpt-4o", tool_available=False)
d.delegate          # False — forced
d.reason            # 'tool_unavailable'
d.explain()         # logs the expected (low) neural accuracy for human review
```

The decision never *fails*; it tells you the expected accuracy so you can log it,
surface a low-confidence flag, or ask the user.

## When this does *not* apply

- **Non-deterministic / open-ended tasks** (creative writing, summarisation,
  judgement). The horizon is about *exact state tracking*, not all reasoning.
- **Shallow subproblems** (d ≪ d\*). Below the horizon, extended reasoning helps —
  don't delegate reflexively.
- **Depth you can't estimate.** Garbage-in: if `estimated_depth` is wrong, the
  decision is wrong. Run BFS / a length estimator first when you can.

## Tuning the knobs

| Parameter | Default | Raise it when… |
|---|---|---|
| `threshold` | 0.5 | you need higher reliability (e.g. 0.8 for safety-critical routing). |
| `margin` | 0.10 | tool calls are expensive and you'll tolerate near-parity neural answers. |
| `tool_accuracy` | 0.92 | you've measured your own tool — use the real number. |

Back to the [documentation hub](README.md).
