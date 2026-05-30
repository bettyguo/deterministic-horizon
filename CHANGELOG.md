# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **World-class interactive learning site** (`docs/index.html`) — the
  dependency-free GitHub Pages app grew from a single explorer into a guided,
  six-section experience: the live horizon explorer (now with a hover tooltip,
  shareable permalinks that encode every slider, one-click PNG export, and a
  "copy Python" button), a **multi-model comparison** chart with toggleable
  decay curves, a **cost-vs-accuracy** panel that shows why tools are 4.2–4.7×
  cheaper per correct solution, an animated **two-theories** ledger, a
  **"think or delegate?" quiz**, and an interactive **three-step theorem
  walkthrough**. Sticky nav, dark/light with persistence,
  `prefers-reduced-motion` support, and keyboard-accessible controls throughout.
- **Practitioner API helpers** in `policy.py`: `should_delegate_batch(...)`
  (vectorised routing for a whole decomposition), `recommend_model(...)`
  (pick the least over-powered model that still clears the threshold at a given
  depth), and `horizon_table()` (sorted per-model d\* / ε₀ / L_eff rows).
- **New CLI commands**: `dh delegate` (one-shot routing decision with a full
  explanation), `dh horizons` (per-model horizon table), and `dh compare-figure`
  (render the per-model decay-curve comparison).
- **`analysis.plot_model_horizons(...)`** — the static, publication-grade twin
  of the web comparison chart; ships as `assets/figure_model_horizons.png` and
  appears in the README.
- Tests for every new helper (`tests/test_policy_extras.py`); the suite is now
  **60 tests** (was 48).
- **Interactive horizon explorer** — the original single-file explorer
  (`docs/horizon-explorer.html` now redirects to `docs/index.html`): live
  sliders for ε₀, γ, L_eff and α that plot the Theorem 4.2 decay curve and
  solve for d\* in real time, plus per-model presets and a delegation
  calculator. Deployable to GitHub Pages.
- **Quickstart notebook** (`notebooks/01_quickstart.ipynb`) — the Colab badge
  target: estimate the horizon offline, fit the decoherence model, and route a
  toy agent in under a minute.
- **Documentation set** under `docs/`: when-to-delegate, theorem cheat-sheet,
  reproducing guide, and FAQ.
- Project meta files: `LICENSE`, `CITATION.cff`, `CONTRIBUTING.md`, this
  changelog, and a `Makefile` with `paper-figures` / `paper-tables` targets.
- **Google Gemini and Together AI model adapters** (`gemini_models.py`,
  `together_models.py`) built on a shared `OpenAICompatibleModel` base — both use
  the providers' OpenAI-compatible endpoints, so the only extra dependency is the
  `openai` client. Registered in `MODEL_REGISTRY`; keys added to `.env.example`.
- Tests: model-registry resolution (`test_models.py`, incl. the exact-match
  guard so `llama-3.1-8b` ≠ `together-llama-3.1-8b`) and an explorer↔policy
  constants sync guard (`test_explorer_sync.py`). Suite is now 48 tests.

### Changed
- Theorem references in `analysis.py` aligned with the camera-ready numbering
  (Thm 1 → Thm 4.2).

### Fixed
- All `ruff` and `black` lint findings across `src/` and `tests/` (the CI lint
  job now passes cleanly).
- Broken relative links in the README (docs, notebook, license, citation).

## [1.0.1] - 2026-05-14

### Changed
- Repository aligned with the ICML 2026 camera-ready paper: theorem numbering,
  per-model horizons, and headline numbers reconciled with Table 3 / Table 5.
- `pyproject.toml` packaging switched to an explicit `package-dir` mapping so the
  flat `src/` layout imports cleanly as `deterministic_horizon`.

## [1.0.0] - 2026-01-29

### Added
- Initial public release: `tasks` (PermutationProbe, FSA-Sim, ArithChain with BFS
  oracles), `models` (OpenAI / Anthropic / DeepSeek / local), `metrics` (SSJ, SFE,
  super-exponential horizon fit, bootstrap CIs), `analysis` (figures + tables),
  `policy` (`should_delegate` / `delegation_decision`), CLI (`dh`), and the
  offline demo.

[Unreleased]: https://github.com/bettyguo/deterministic-horizon/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/bettyguo/deterministic-horizon/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/bettyguo/deterministic-horizon/releases/tag/v1.0.0
