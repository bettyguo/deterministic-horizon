---
title: "[docs] Record a 30-second GIF of the offline demo for the README"
labels:
  - documentation
  - good-first-issue
milestone: "v1.0.1"
---

## Context

The README leads with `examples/demo.py` and claims a 60-second offline reproduction of the Deterministic Horizon. A visitor who lands on the repo has to either (a) take our word for it or (b) install the package to see anything. A 30-second screencast/GIF above the hero figure would convert curious readers into stars and clones at much higher rates.

## What needs to happen

Record a short, silent, looping GIF (≤ 5 MB) that shows:

1. `python examples/demo.py` being run in a terminal.
2. The depth/accuracy table scrolling out.
3. The final `d* = … (R² = …)` print line.
4. The generated `analysis/figure_decay.png` opening (or being shown as the next frame).

Total runtime ≤ 30 seconds, smaller is better. Save it to `assets/demo.gif`. Tools that work well: [VHS](https://github.com/charmbracelet/vhs), [asciinema + agg](https://github.com/asciinema/agg), or [terminalizer](https://github.com/faressoft/terminalizer).

## Acceptance criteria

- [ ] `assets/demo.gif` checked in, ≤ 5 MB.
- [ ] README has the GIF placed just below the `## 60-second offline demo` heading.
- [ ] GIF is readable at 720p on GitHub's rendered README.
- [ ] If VHS was used, the `.tape` source is also committed under `assets/`.

## Hints

- VHS produces deterministic recordings, which is nice for re-shoots after a code change.
- Keep the demo command in the GIF identical to the one in the README to avoid drift.
