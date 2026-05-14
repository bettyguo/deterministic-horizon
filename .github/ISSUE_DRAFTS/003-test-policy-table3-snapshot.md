---
title: "[test] Snapshot-test `MODEL_HORIZONS` against paper Table 3"
labels:
  - tests
  - good-first-issue
milestone: "v1.0.1"
---

## Context

The per-model constants in [`src/deterministic_horizon/policy.py`](../../src/deterministic_horizon/policy.py) (`MODEL_HORIZONS`) come from Table 3 of the paper. Right now there's no test that pins them — a future contributor could nudge them and the tests would still pass even though the predictions would diverge from the published numbers.

## What needs to happen

Add `tests/test_policy_snapshot.py` that asserts the `MODEL_HORIZONS` table matches a JSON snapshot. The snapshot lives in `tests/snapshots/model_horizons.json` and is verbatim Table 3.

## Acceptance criteria

- [ ] `tests/snapshots/model_horizons.json` exists, mirrors the current `MODEL_HORIZONS` dict, and has a header comment pointing to the paper section.
- [ ] `tests/test_policy_snapshot.py` loads both and asserts equality with a clear `assert MODEL_HORIZONS == loaded, "Updated paper values? Refresh the snapshot."` failure message.
- [ ] If the snapshot is updated, the PR description must cite which seed / replication produced the new numbers.

## Hints

- Use `pytest.approx` for the float comparisons — JSON serialisation can introduce trailing-zero noise.
- Keep the snapshot file tiny (one dict, pretty-printed).
