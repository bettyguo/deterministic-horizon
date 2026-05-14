---
title: "[feat] Interactive `should_delegate` demo on Hugging Face Spaces"
labels:
  - enhancement
  - help-wanted
  - demo
milestone: "v1.1.0"
---

## Context

The `should_delegate` API is the part of this project most useful to engineers — but they have to `pip install` it to try it. A Hugging Face Space with two sliders (depth, model) and a live-rendered expected-accuracy curve would be the lowest-friction way to demonstrate the policy.

## What needs to happen

1. Add `spaces/horizon-explorer/app.py` (Gradio) that exposes:
   - A dropdown for model (filled from `MODEL_HORIZONS`).
   - A depth slider (0 → 50).
   - A live-updating curve of `expected_neural_accuracy(d, model)` overlaid with the chosen depth.
   - The output of `delegation_decision(...).explain()` underneath.
2. Add `spaces/horizon-explorer/README.md` with the Space's metadata header.
3. Document the Space URL in the main `README.md`.

## Acceptance criteria

- [ ] The Space runs on the free CPU tier (no GPU needed — it's pure NumPy/matplotlib).
- [ ] Cold-start under 30 seconds.
- [ ] The curve updates as you drag the sliders.
- [ ] The README links the Space.

## Hints

- Gradio's `gr.Blocks` with `live=True` is the easiest path.
- The Space can install this package directly: `pip install git+https://github.com/deterministic-horizon/deterministic-horizon`.
- Use `matplotlib`'s `Agg` backend, render to a PNG, and return via `gr.Image` — avoids the Plotly dependency.
