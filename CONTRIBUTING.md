# Contributing to Deterministic Horizon

Thanks for thinking about contributing — this is an active research codebase and
extensions are welcome.

## Quick start

```bash
git clone https://github.com/bettyguo/deterministic-horizon
cd deterministic-horizon
pip install -e ".[dev,all]"
pre-commit install
pytest -m "not slow and not api"
```

## What we're looking for

High-value contributions, in rough order of priority:

1. **New tasks** — anything with a deterministic operator semantics and BFS oracle. See `src/deterministic_horizon/tasks/permutation.py` for a 200-line reference.
2. **New model adapters** — Gemini, Mistral, Reka, etc. Follow the `BaseModel` interface in `src/deterministic_horizon/models/base.py`.
3. **Architecture studies** — Mamba/RWKW/MoE decoherence experiments. Hypothesis: $d^* \propto \sqrt{\text{effective state capacity}}$.
4. **Real-world task adapters** — SWE-Bench-State, WebArena-Nav, SQL-Multi are stubbed; full implementations welcome.
5. **Visualisation** — interactive horizon explorer, Hugging Face Spaces demo.

If you're not sure whether something is in scope, open an issue first.

## Style

- Code is formatted with **ruff** + **black** (line length 100). `pre-commit` enforces it.
- Type hints required on public APIs; encouraged everywhere.
- No `print` in library code — use `logging`.
- Tests required for new public functions. We aim for ~80% line coverage.

## Tests

```bash
pytest                           # everything (no slow/api tests)
pytest -m slow                   # slow tests (real BFS at depth 40+)
pytest -m api                    # tests that hit live APIs (requires .env)
pytest --cov=src/deterministic_horizon --cov-report=term-missing
```

## Pull request checklist

- [ ] `pytest` passes
- [ ] `ruff check` is clean
- [ ] New features have tests
- [ ] `README.md` / `docs/` updated if user-visible
- [ ] If the change affects numbers in the paper, run `make paper-tables` and check `results/sample/` diffs are intentional

## Reporting issues

When filing a bug, please include:

- Python version and platform
- `pip freeze | grep -E "openai|anthropic|torch|transformers"` if model-related
- Minimal repro (ideally a 10-line script)
- Expected vs. observed behaviour

## Code of conduct

Be excellent. We follow the [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Violations: open a confidential issue or email the maintainers.
