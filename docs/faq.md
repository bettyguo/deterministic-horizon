# FAQ

### Is the offline demo cherry-picked?

No. The demo uses a *synthetic* reasoner whose per-step error follows the exact
context-dependent model of Theorem 4.2 — it's a controlled illustration of the
mechanism, not a benchmark result. The cross-model **empirical** numbers come
from real API calls: 12 models × 5 conditions × 8 tasks × 500 instances × 3 seeds
≈ 720,000 evaluations (~\$3,420). See [reproducing](reproducing.md).

### How is this different from "transformers can't do X" (expressivity) papers?

Expressivity work proves what transformers *cannot compute in principle*
(asymptotic $\text{TC}^0$ statements). We characterise what frontier models
*cannot reliably execute in practice* at the depths real systems run at, give a
**closed-form** bound (d\* ≈ 22 steps), and prove fine-tuning cannot move it. The
Deterministic Horizon is a usable engineering quantity, not an asymptotic.

### Does this mean reasoning models are useless?

The opposite — it tells you exactly *when* to use them. Below d\*, extended
reasoning helps. Past d\*, it degrades and tools win by 50–70 points. The
contribution is knowing the boundary. See [when to delegate](when-to-delegate.md).

### Why isn't a 100k-token context window enough?

Because the limit isn't the raw context length $L$ — it's the **effective
decoherence length** $L_{\text{eff}} \approx O(10^2)$ steps over which attention
keeps *usable* state resolution. You can fit the tokens in the window and still
lose the state. This is Definition 4.1 / Theorem 4.4.

### How is this different from the "overthinking" / Simplicity Bias work?

[Wu et al., 2025](https://arxiv.org/abs/2503.16419) attribute the inverted-U to a
trained *preference* for short outputs — which fine-tuning should fix. We propose
a complementary **architectural** diagnosis: even a model that *tries* to reason
long can't keep state. The two theories make four divergent, falsifiable
predictions; the data backs the architectural one (e.g. fine-tuning recovery
3.2% vs. the > 30% the preference theory predicts). See the
[theorem cheat-sheet](theorem-cheatsheet.md).

### What tasks does the horizon apply to?

Deterministic, exact-state-tracking problems: permutation sorting, finite-state
simulation, arithmetic chains, BFS-style search — anything with a *unique correct
intermediate state* at each step. It does **not** describe open-ended or
judgement tasks where there's no single correct trace.

### My model isn't in the table. What horizon do I get?

The `"default"` parameters (d\* = 24, the midpoint of the measured [19, 31]
range). For a real number, run the empirical pipeline on your model, or override
`(ε₀, L_eff)` directly in `expected_neural_accuracy`. See
[when to delegate](when-to-delegate.md#per-model-horizons).

### How do I cite this?

See [`CITATION.cff`](../CITATION.cff) (GitHub's "Cite this repository" button uses
it) or the BibTeX block in the [README](../README.md#citation).

### Where do I report a bug or request a task/model adapter?

Open an issue (templates are wired up under [`.github/`](../.github/)) and see
[`CONTRIBUTING.md`](../CONTRIBUTING.md). Several drafts in
[`.github/ISSUE_DRAFTS/`](../.github/ISSUE_DRAFTS/) are tagged *good first issue*.

Back to the [documentation hub](README.md).
