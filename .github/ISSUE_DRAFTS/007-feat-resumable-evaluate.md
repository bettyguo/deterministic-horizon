---
title: "[feat] Resumable `dh evaluate` from a partial results JSON"
labels:
  - enhancement
  - help-wanted
  - reliability
milestone: "v1.1.0"
---

## Context

A full sweep (12 models × 5 conditions × 500 instances) takes ~36 hours and is interrupted often — by API outages, rate limits, or the maintainer's laptop sleeping. Today, `dh evaluate` writes the whole JSON only at the end, so any interruption means starting over.

## What needs to happen

Make `dh evaluate` resumable:

1. After each instance × condition pair, append the result to `<output>.partial.jsonl` (newline-delimited JSON).
2. On start-up, if `--output` points at a file whose `.partial.jsonl` sidecar exists, load it and skip the already-evaluated `(instance_id, condition)` pairs.
3. On clean finish, consolidate the `.partial.jsonl` into the final `--output` JSON array and delete the sidecar.

## Acceptance criteria

- [ ] Killing `dh evaluate` mid-run and re-running it produces the same final output as a single uninterrupted run (deterministic seeds).
- [ ] A new `--resume / --no-resume` flag, with `--resume` the default. `--no-resume` deletes the sidecar before starting.
- [ ] Test under `tests/test_runners.py` that simulates a kill via `monkeypatch` raising after the 5th instance and checks that the resumed run completes the remaining 5.

## Hints

- The append-only `jsonl` sidecar is cheaper than re-serialising a growing list — important for 500+ instances.
- Look at how [`runners.run_evaluation`](../../src/deterministic_horizon/runners.py) iterates `(instance, condition)` pairs — adding a `skip_keys` set is the surgical change.
