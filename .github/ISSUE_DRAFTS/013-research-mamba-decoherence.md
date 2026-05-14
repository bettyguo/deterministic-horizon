---
title: "[research] Mamba / SSM decoherence study — does d* scale differently?"
labels:
  - research
  - help-wanted
  - architecture-study
milestone: "v1.3.0"
---

## Context

Theorem 1 (the per-step error model) is derived for decoder-only attention. State-space models share the $\text{TC}^0$ ceiling (Merrill 2024) but have a different capacity bound: roughly `O(d_state)` distinct trackable states, where `d_state` is the recurrent state dimension. We sketched preliminary results in Appendix D; this issue is the full study.

The headline question: **does the horizon for Mamba-style models depend on `d_state` (linear in state size) or on `L` (context-dependent like attention)?** The two hypotheses make different predictions about $d^\star$ scaling, and they're separable empirically.

## What needs to happen

1. Add a Mamba-2 model adapter (we already have `LocalModel`; this is a thin specialisation that exposes `d_state` and a few SSM-specific knobs).
2. Run the standard sweep (C1, C2, C3, C4) on `state-spaces/mamba-2.8b` and `state-spaces/mamba-130m`.
3. Fit the decoherence model with `context_length` replaced by `d_state` and compare R² to the attention fit.
4. Write a short companion note (`docs/research/mamba-decoherence.md`) summarising the findings.

## Acceptance criteria

- [ ] At least two Mamba models evaluated end-to-end.
- [ ] Comparative R² for the two competing fits reported.
- [ ] If the SSM-specific fit wins, propose a `MambaHorizon` extension to `policy.py` so practitioners can route between SSM and attention models correctly.

## Hints

- Mamba inference is ~3× slower than equivalent-parameter transformers on the standard HF stack — budget GPU-hours accordingly.
- The official Mamba repo has a faster `selective_scan_cuda` kernel; use it if you can.
- This is a paper-grade contribution and will be co-credited.
