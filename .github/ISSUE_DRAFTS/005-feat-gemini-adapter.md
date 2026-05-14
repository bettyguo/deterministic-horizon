---
title: "[feat] Gemini 1.5/2.0 model adapter"
labels:
  - enhancement
  - help-wanted
  - models
milestone: "v1.1.0"
---

## Context

We ship adapters for OpenAI, Anthropic, DeepSeek, and local HF models, but Gemini is conspicuously missing. Several research questions in the paper would be more compelling with Gemini 1.5 Pro and Gemini 2.0 Flash numbers — particularly the cross-architecture decoherence claim.

## What needs to happen

1. Add `src/deterministic_horizon/models/gemini_models.py` with a `GeminiModel(BaseModel)` subclass.
2. Implement `generate(...)` and `generate_with_tools(...)` matching the existing `BaseModel` contract; the tool format Google uses differs from OpenAI's, so a small translator is needed.
3. Register `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash` in `MODEL_REGISTRY` in [`src/deterministic_horizon/models/__init__.py`](../../src/deterministic_horizon/models/__init__.py).
4. Add a `gemini` optional dependency group in `pyproject.toml` pinning `google-genai`.
5. Run the C1 condition on `gemini-1.5-pro` for `data/sample/permutation_n8.json` and add the resulting `d*` and decoherence-fit to `MODEL_HORIZONS` in `policy.py`.

## Acceptance criteria

- [ ] `pip install -e ".[gemini]"` works.
- [ ] `dh list-models` shows the three Gemini entries.
- [ ] `dh evaluate --model gemini-1.5-pro …` works when `GEMINI_API_KEY` is set.
- [ ] At least one Gemini entry added to `MODEL_HORIZONS` with the empirical `(eps0, gamma, d_star)` triple.
- [ ] Smoke test in `tests/test_models_gemini.py` (mocked HTTP, marked `api`).

## Hints

- The Anthropic adapter in [`anthropic_models.py`](../../src/deterministic_horizon/models/anthropic_models.py) is the cleanest reference, including how it handles tool calls.
- Google's tool schema uses `functionDeclarations`; the translator should accept the OpenAI-style schema we already emit from tasks.
- Cost note: at our standard sweep (~12,000 calls), `gemini-1.5-pro` is approximately $40 — well within the typical research budget.
