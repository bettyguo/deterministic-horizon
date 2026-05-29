# Changelog

All notable changes to this project are documented in this file. This project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] — 2026-05-29

Camera-ready consistency pass: align every formula, constant, and dataset with
the accepted paper.

### Changed
- **Decoherence formula now uses the effective decoherence length $L_{\text{eff}}$**
  (not the raw context window) throughout `policy.py`, `analysis.decay_curve`,
  and `metrics.fit_decoherence_model`. The paper is explicit that
  $L_{\text{eff}}=O(10^2)$ steps $\ll L=O(10^5)$ tokens; using raw $L$ erased the
  quadratic term and predicted near-perfect accuracy.
- **`MODEL_HORIZONS` rebuilt from the paper's measured $d^*$** (PermutationProbe
  Table 3 + architecture-ablation Table 5). Each model's $(\varepsilon_0, L_{\text{eff}})$
  is calibrated so the decay curve crosses 0.5 exactly at its reported $d^*$;
  GPT-4o reproduces the paper's $\varepsilon_0=0.02,\gamma=0.15,L_{\text{eff}}=150,d^*\approx22.3$.
- **PermutationProbe operators are now the canonical adjacent transpositions**
  ($S_n$, diameter $C(n,2)$); `generate_instance` produces instances whose
  `optimal_depth` is the true BFS-optimal depth (paper Appendix algorithm),
  instead of a possibly-non-minimal random-walk length.
- Model identifiers/IDs corrected to the paper's Reproducibility checklist
  (`Llama-3.1-8B`, `claude-sonnet-4-5-…`, HF IDs for the open-weight suite);
  `max_tokens` default 8192; fine-tuning config set to the paper's Llama-3.1-8B,
  batch size 8, cosine schedule.
- `generate_tables` estimates the horizon on neural CoT (C1) only, never pooled
  with the always-correct tool condition.
- Regenerated `data/sample/` and `results/sample/` (with SSJ precision/recall),
  and the committed figures/tables, from the corrected pipeline ($d^*\approx21$,
  fit $R^2\approx0.98$). Added `scripts/regenerate_sample_data.py`.
- Documentation, README, notebook, and packaging metadata updated for accuracy
  (repository URL, camera-ready PDF link, paper-consistent numbers and authors).

## [1.0.0] — 2026-05-14

Initial public release accompanying the ICML 2026 paper *"The Deterministic
Horizon: When Extended Reasoning Fails and Tool Delegation Becomes Necessary"*.

### Added
- Five experimental conditions (C1–C5): neural CoT, direct, tool-integrated, length-encouraged, fine-tuned
- Three task families: `PermutationTask`, `FSATask`, `ArithmeticTask` — each with a BFS oracle
- Unified model interface across OpenAI / Anthropic / DeepSeek / local HF models
- State-Space Jaccard (SSJ) metric with precision/recall decomposition
- Step-to-First-Error (SFE) metric
- Super-exponential decay fit (Theorem 1) and bootstrap CI for the Deterministic Horizon $d^*$
- Cross-model correlation analysis
- `dh` CLI (`generate`, `evaluate`, `analyze`, `train`)
- **Practitioner decision helpers** — `should_delegate()`, `delegation_decision()`,
  `expected_neural_accuracy()`, `horizon_for()` — turn Theorem 1 into a single-line
  branch you can paste into an agent's planner loop
- Offline demo (`examples/demo.py`) — no API keys required, ~10 seconds runtime
- Production-pattern example (`examples/agent_routing.py`) — end-to-end agent
  routing using `should_delegate`, no API keys required
- Quickstart notebook (`notebooks/01_quickstart.ipynb`)
- Pre-generated sample instances + sample results for one-click reproduction
- Documentation under `docs/`: when-to-delegate, theorem cheat-sheet,
  architecture overview, reproducing guide, FAQ
- Continuous integration (GitHub Actions) on Linux + macOS + Windows
  with lint + tests + wheel build
- Issue / PR templates, Code of Conduct, Dependabot, and link-check workflow
- Optional dependency groups: `[openai]`, `[anthropic]`, `[local]`, `[viz]`, `[dev]`, `[all]`

### Reproducibility
- All experiments seeded with `{42, 2024, 2025}`
- Wilson score CIs for binomial proportions
- Holm–Bonferroni multiple-comparison correction
- TOST equivalence testing for null-result claims
