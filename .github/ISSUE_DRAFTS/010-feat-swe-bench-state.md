---
title: "[feat] SWE-Bench-State task adapter"
labels:
  - enhancement
  - help-wanted
  - research
  - new-task
milestone: "v1.2.0"
---

## Context

The roadmap promises a SWE-Bench-State integration: each ticket becomes an instance whose "depth" is the number of distinct files / functions / state variables an agent must track to produce a correct patch. This is the most direct way to validate the Deterministic Horizon prediction on a real production-grade benchmark.

The paper's claim is that on tickets with depth > d* the gap between an agent that uses a static-analysis tool (LSP / treesitter) and one that does pure CoT is at least 30 percentage points — exactly the gap we observe on permutation puzzles.

## What needs to happen

1. Add `src/deterministic_horizon/tasks/swe_bench_state.py` implementing `BaseTask`.
2. Define the operator semantics: `read_file`, `edit_function`, `add_import`, `delete_function`, etc. The full set is in §A.3 of the paper's appendix.
3. Implement a `bfs_solve` proxy — for SWE-Bench-State we don't have an exact BFS oracle, so use the ground-truth patch from the dataset as the optimal trajectory and define `optimal_depth` as the number of distinct edits in that patch.
4. Add a `swe-bench-state` entry to the configs.

## Acceptance criteria

- [ ] `dh generate --task swe-bench-state --output data/swe_state.json` loads 100 sample tickets from the existing SWE-Bench dataset.
- [ ] `dh evaluate --model claude-4.5-opus --task swe-bench-state --conditions C1,C3 …` runs end-to-end on the 100 sample tickets.
- [ ] The resulting accuracy-vs-depth curve recovers a horizon roughly consistent with the paper's predictions for `claude-4.5-opus`.

## Hints

- This is a research-scale issue — expect 1–2 person-weeks of work, not an afternoon.
- The C3 tool for this domain is a `read_file` + `edit_function` pair that exposes the real file system, sandboxed.
- Coordinate with the maintainers before starting — there's an unpublished evaluation script we can share to bootstrap.
