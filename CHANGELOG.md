# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Explorer accessibility, touch & teaching upgrades** (`docs/index.html`):
  the main decay chart now shades the **reason zone** (left of `d*`) and
  **delegate zone** (right of `d*`) and labels the tool and threshold lines
  directly on the canvas, so the core lesson reads at a glance. Both canvas
  charts moved from mouse-only to **pointer events** (mouse + touch + pen), so
  the hover probe and the multi-model scrubber now work on phones and tablets.
  The explorer chart is **keyboard-operable**: focus it and use `←`/`→`
  (`Shift` = ±5, `Home`/`End` to jump) to move the depth probe, with a visible
  focus ring and a live decision readout. The hover tooltip now also calls the
  reason/delegate verdict at the probed depth.
- **World-class interactive learning site** (`docs/index.html`) — the
  dependency-free GitHub Pages app grew from a single explorer into a guided,
  seven-section experience: the live horizon explorer (now with a hover tooltip,
  shareable permalinks that encode every slider, one-click PNG export, and a
  "copy Python" button), a **multi-model comparison** chart — now with a hover
  scrubber that ranks every model's accuracy at the depth under the cursor — a
  **cost-vs-accuracy** panel that shows why tools are 4.2–4.7× cheaper per
  correct solution, an **agent decomposition planner** that visualises
  `should_delegate_batch(...)` end-to-end (add sub-goal depths and watch the
  policy route each step, with all-neural vs. policy-routed success probabilities
  multiplied across the chain), an animated **two-theories** ledger, a
  **"think or delegate?" quiz** (now with streak/best tracking, randomised
  scenarios, and full keyboard play), and an interactive **three-step theorem
  walkthrough**. Sticky nav, dark/light with persistence, `aria-live` regions,
  `prefers-reduced-motion` support, and keyboard-accessible controls throughout.
  A headless Playwright pass confirms zero console errors across every section.
- **Live sensitivity ("what moves the horizon?") panel** in the explorer — a
  tornado view that ranks how far `d*` shifts when each parameter (ε₀, γ, L_eff,
  α) is nudged ±20% from the current setting, updating in real time as you drag.
- **Native MathML equations** for the three-step theorem walkthrough — crisp,
  zero-dependency typeset math (no KaTeX/MathJax) with `aria-label` fallbacks.
- **Lint**: `ruff check .` is now fully green across the repo, including the
  quickstart notebook (sorted imports, no multi-statement lines).
- **Shareability & SEO for the site**: a `summary_large_image` social card
  (`docs/og-image.png`), Open Graph / Twitter image + description tags,
  schema.org `ScholarlyArticle` JSON-LD, a canonical link, and first-visit
  respect for the OS `prefers-color-scheme` (saved preference still wins).
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
- Tests for every new helper (`tests/test_policy_extras.py`), plus a Node-backed
  JavaScript syntax guard for the explorer (`test_explorer_javascript_parses`,
  skipped when Node is unavailable); the suite is now **61 tests** (was 48).
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
