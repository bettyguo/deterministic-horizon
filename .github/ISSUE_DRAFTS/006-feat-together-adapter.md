---
title: "[feat] Together AI adapter for cheap open-weight evaluations"
labels:
  - enhancement
  - help-wanted
  - models
milestone: "v1.1.0"
---

## Context

The paper's open-weight evaluations (Llama 3.1, Qwen 2.5, DeepSeek) were run via Together AI credits. Right now the only way to evaluate them is through `LocalModel`, which requires GPUs. A `TogetherModel` adapter would let any contributor reproduce those numbers for the cost of a few API calls.

## What needs to happen

1. Add `src/deterministic_horizon/models/together_models.py` with a `TogetherModel(BaseModel)` subclass — Together's API is OpenAI-compatible, so this should largely subclass `OpenAIModel` with a different base URL and key env var.
2. Register the open-weight models we evaluated in the paper:
   `meta-llama/Llama-3.1-70B-Instruct-Turbo`,
   `Qwen/Qwen2.5-72B-Instruct-Turbo`,
   `mistralai/Mixtral-8x22B-Instruct-v0.1`.
3. Add a `together` extra in `pyproject.toml`.
4. Document the API-key flow in `.env.example` and `docs/reproducing.md`.

## Acceptance criteria

- [ ] `dh evaluate --model llama-3.1-70b …` works when `TOGETHER_API_KEY` is set.
- [ ] The README "What's inside" / model coverage table mentions Together.
- [ ] Existing tests don't regress; `tests/test_models_together.py` smoke-tests the adapter with `responses` HTTP mocking.

## Hints

- Together's OpenAI compatibility means you can probably subclass `OpenAIModel` and only override `__init__` to set `base_url="https://api.together.xyz/v1"` and `api_key=os.environ["TOGETHER_API_KEY"]`.
- Watch out for the model names — Together uses `meta-llama/Llama-3.1-70B-Instruct-Turbo` (with the `Turbo` suffix for the quantised serving path), not `llama-3.1-70b`. Expose the user-friendly short name in `MODEL_REGISTRY` and translate internally.
