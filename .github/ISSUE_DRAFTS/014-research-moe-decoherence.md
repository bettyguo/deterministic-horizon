---
title: "[research] MoE decoherence: does expert specialisation shift d*?"
labels:
  - research
  - help-wanted
  - architecture-study
milestone: "v1.3.0"
---

## Context

Mixture-of-Experts models route each token through a subset of experts. Naively, this should *not* change the per-head attention bottleneck — but if individual experts specialise on state-tracking subroutines, the effective tracking capacity could be substantially larger than the bound in Theorem 2 suggests. Or smaller, if the routing introduces noise.

The neat experimental design: compare a dense and an MoE-trained model with matched total parameters (e.g. Mixtral 8x22B vs. a hypothetical dense 22B-active-params baseline) on the permutation sweep and see whether $d^\star$ shifts.

## What needs to happen

1. Pick a clean dense/MoE pair. Candidates: `Mixtral-8x22B-Instruct` vs `Llama-3.1-70B-Instruct` (both via Together, see #006).
2. Run the full sweep (C1–C4) on both.
3. Fit the decoherence model and compare $(\varepsilon_0, \gamma, d^\star)$.
4. If you find a shift, instrument the experts: which expert handles each step? Is there a "state-tracking expert"?
5. Write `docs/research/moe-decoherence.md`.

## Acceptance criteria

- [ ] Both models evaluated end-to-end on `data/sample/permutation_n8.json`.
- [ ] Side-by-side decoherence-fit comparison plot in the docs.
- [ ] If a shift is detected, an attempt at mechanistic explanation (routing-statistics analysis).
- [ ] Numbers added to `MODEL_HORIZONS`.

## Hints

- Comparing across model families is messier than comparing within one — calibrate on a non-state-tracking benchmark first to control for general capability gaps.
- The routing-stats analysis requires access to the experts' top-k decisions; for HF models that's straightforward, for closed APIs it isn't.
- Co-credit on the follow-up paper for substantial contributions.
