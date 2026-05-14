---
title: "[bug] `dh train` is a stub — wire it to `deterministic_horizon.training.finetune`"
labels:
  - bug
  - good-first-issue
milestone: "v1.0.1"
---

## Context

The CLI exposes a `train` subcommand:

```bash
$ dh train --config configs/finetune.yaml --output-dir checkpoints/
[bold blue]Fine-tuning not yet implemented in CLI[/]
Use the Python API: deterministic_horizon.training.finetune()
```

But the underlying Python entry point [`src/deterministic_horizon/training/finetune.py`](../../src/deterministic_horizon/training/finetune.py) is fully implemented (~500 LOC). The CLI just doesn't call it. That's confusing for anyone trying to reproduce the C5 condition from the paper.

## What needs to happen

1. Load the YAML config via `deterministic_horizon.config.load_config`.
2. Resolve the trace dataset, base model, LoRA config (or full fine-tune), seeds.
3. Call `deterministic_horizon.training.finetune.run(...)` with the resolved arguments.
4. Stream progress via the existing `rich.Progress` machinery used by `evaluate`.
5. Write the resulting checkpoint and a `train_metrics.json` under `--output-dir`.
6. Add an `examples/finetune_smoke.py` that runs the loop for ~5 steps on a tiny synthetic dataset, so CI can smoke-test it without GPUs.

## Acceptance criteria

- [ ] `dh train --config configs/finetune.yaml --output-dir <tmp>` produces a checkpoint and a `train_metrics.json` in `<tmp>` on CPU when the config selects a small model.
- [ ] A new test under `tests/test_training.py` exercises the CLI path with a 2-layer toy model.
- [ ] Error path: missing config file → friendly message, non-zero exit code.

## Hints

- The existing `evaluate` command in [`cli.py`](../../src/deterministic_horizon/cli.py) is the right shape to copy.
- Mark the new test with `@pytest.mark.slow` so the default `pytest -m "not slow"` skips it.
