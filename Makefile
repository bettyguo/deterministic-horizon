# Deterministic Horizon — developer shortcuts.
# Cross-platform: targets call `python` so they work on Linux/macOS/Windows.

PY ?= python

.DEFAULT_GOAL := help
.PHONY: help install dev test lint fmt demo paper-figures paper-tables sample clean

help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install:  ## Editable install (core only, no LLM SDKs).
	$(PY) -m pip install -e .

dev:  ## Editable install with dev + viz extras.
	$(PY) -m pip install -e ".[all,dev]"

test:  ## Run the unit test suite.
	$(PY) -m pytest -q -m "not slow and not api"

lint:  ## Ruff + Black (check only) — same as CI.
	$(PY) -m ruff check src tests
	$(PY) -m black --check src tests

fmt:  ## Auto-format and auto-fix.
	$(PY) -m ruff check src tests --fix
	$(PY) -m black src tests

demo:  ## Run the offline horizon demo (writes analysis/figure_decay.png).
	$(PY) examples/demo.py

paper-figures:  ## Regenerate assets/figure_*.png from results/sample/.
	$(PY) scripts/regenerate_sample_data.py --figures

paper-tables:  ## Regenerate analysis/*.{md,json} from results/sample/.
	$(PY) scripts/regenerate_sample_data.py --tables

sample:  ## Regenerate all deterministic sample artefacts.
	$(PY) scripts/regenerate_sample_data.py

clean:  ## Remove caches and build artefacts.
	$(PY) -c "import shutil,glob,os; [shutil.rmtree(p,ignore_errors=True) for p in glob.glob('**/__pycache__',recursive=True)+['.ruff_cache','.pytest_cache','build','dist']]"
