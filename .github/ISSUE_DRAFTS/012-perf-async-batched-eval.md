---
title: "[perf] Async-batched evaluation for OpenAI / Anthropic adapters"
labels:
  - performance
  - help-wanted
  - enhancement
milestone: "v1.2.0"
---

## Context

Today `runners.run_evaluation` is sequential: one instance × condition pair at a time. On a 500-instance, 4-condition sweep that's 2000 round-trips per model. Even at 1 second/call we'd run for 33 minutes per model. The OpenAI and Anthropic APIs both support meaningful concurrency (≥ 50 in-flight), and we leave it on the table.

## What needs to happen

1. Add an `async_generate(...)` method on `BaseModel`, with default fallback running the sync version in a thread.
2. Implement it on `OpenAIModel` and `AnthropicModel` using the providers' native async clients.
3. Add `runners.run_evaluation_async(...)` that uses `asyncio.gather` with a configurable concurrency cap (default 20) and respects token-bucket rate limits per provider.
4. Expose a `--concurrency N` flag on `dh evaluate`.

## Acceptance criteria

- [ ] `dh evaluate --model gpt-4o --instances data/sample/permutation_n8.json --concurrency 20` completes the sample sweep ≥ 5× faster than `--concurrency 1` on the same machine.
- [ ] Rate-limit 429s are retried with exponential backoff (we already have `tenacity` as a dependency).
- [ ] Existing tests pass; new tests under `tests/test_runners_async.py` use `asyncio` to verify ordering and timeout behaviour.

## Hints

- Set `concurrency=1` as the safe default for now; users opt-in.
- Keep the sync `run_evaluation` available as a thin wrapper around the async path.
- Watch out for tool-call sessions in the C3 condition — each instance needs its own session, and they're stateful, so they can't share state across the async pool.
