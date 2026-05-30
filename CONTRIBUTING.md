# Contributing to Deterministic Horizon

Thanks for your interest! This repository accompanies the ICML 2026 paper
*The Deterministic Horizon*. Bug reports, new task adapters, model adapters, and
analysis extensions are all welcome.

## Ground rules

- Be respectful and constructive. We follow the spirit of the
  [Contributor Covenant](https://www.contributor-covenant.org/).
- Keep the offline path dependency-free: the core (`metrics`, `policy`,
  `analysis`, `tasks`) must import and run **without** any LLM SDK installed.
- Every new public function gets a docstring and a test. The math in `policy.py`
  and `metrics/` must stay in exact agreement with the paper's theorems.

## Development setup

```bash
git clone https://github.com/bettyguo/deterministic-horizon
cd deterministic-horizon
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Before you open a PR

Run the same checks CI runs — they must all pass:

```bash
ruff check src tests        # lint
black --check src tests     # formatting
pytest -q                   # unit tests (32+ should pass)
python examples/demo.py     # offline smoke test (writes analysis/figure_decay.png)
```

Or in one shot with the Makefile targets, if you have `make`:

```bash
make lint
make test
```

## What makes a good contribution

| Area | Examples | Notes |
|---|---|---|
| **Tasks** | New `BaseTask` subclass (SWE-Bench-State, SQL-Multi, WebArena-Nav) | Must expose a BFS/oracle so `optimal_depth` is the *true* optimum. |
| **Models** | New adapter under `src/models/` | Subclass `BaseModel`; keep the import lazy so the core stays SDK-free. |
| **Metrics** | New diagnostic in `src/metrics/` | Add a unit test pinning it against a closed-form value. |
| **Docs** | Clarifications, fixes, translations | Keep links relative; the `Docs` workflow runs a markdown link check. |

Open issues are tracked under [`.github/ISSUE_DRAFTS/`](.github/ISSUE_DRAFTS/) and
the live issue tracker — several are tagged *good first issue*.

## Commit & PR conventions

- One logical change per PR; keep diffs reviewable.
- Reference the issue you're closing (`Closes #NN`).
- The PR template ([`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md))
  has a short checklist — please fill it in.

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE) that covers this project.
