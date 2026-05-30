# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Interactive horizon explorer** (`docs/horizon-explorer.html`) — a
  dependency-free, single-file web app with live sliders for ε₀, γ, L_eff and α
  that plots the Theorem 4.2 decay curve and solves for d\* in real time, plus
  per-model presets and a delegation calculator. Deployable to GitHub Pages.
- **Quickstart notebook** (`notebooks/01_quickstart.ipynb`) — the Colab badge
  target: estimate the horizon offline, fit the decoherence model, and route a
  toy agent in under a minute.
- **Documentation set** under `docs/`: when-to-delegate, theorem cheat-sheet,
  reproducing guide, and FAQ.
- Project meta files: `LICENSE`, `CITATION.cff`, `CONTRIBUTING.md`, this
  changelog, and a `Makefile` with `paper-figures` / `paper-tables` targets.

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
