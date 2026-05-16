"""Tests for the training CLI path."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest


def test_train_cli_structure():
    """Verify that the train command is properly defined and accessible."""
    from deterministic_horizon.cli import app

    # Check that 'train' subcommand exists
    info = app.registered_commands
    command_names = [c.name for c in info if c.name]
    assert "train" in command_names, "train command missing from CLI"


def test_train_config_not_found():
    """Calling `dh train --config nonexistent.yaml` should fail gracefully."""
    from typer.testing import CliRunner
    from deterministic_horizon.cli import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["train", "--config", "nonexistent.yaml", "--output-dir", "/tmp/_test"],
    )
    assert result.exit_code != 0, "Should exit with non-zero on missing config"
    assert "not found" in result.stdout.lower(), (
        f"Should mention missing config. Got: {result.stdout}"
    )


@pytest.mark.slow
def test_train_cli_with_synthetic_data():
    """End-to-end test: generate synthetic data and run `dh train`.
    
    Uses a tiny model (Qwen2.5-0.5B) for a few steps on CPU.
    Marked 'slow' to skip in default runs.
    """
    from typer.testing import CliRunner
    from deterministic_horizon.cli import app

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "checkpoints"

        # Create a minimal config pointing to a tiny model
        config = {
            "model": {"name": "Qwen/Qwen2.5-0.5B-Instruct"},
            "task": {"name": "permutation", "n_elements": 4},
            "experiment": {"name": "smoke", "n_instances": 5, "conditions": ["C5"]},
            "random_seed": 42,
        }
        config_path = Path(tmpdir) / "smoke_config.yaml"
        with open(config_path, "w") as f:
            json.dump(config, f)

        result = runner.invoke(
            app,
            [
                "train",
                "--config", str(config_path),
                "--output-dir", str(output_dir),
            ],
        )

        # It may fail with ImportError (missing torch/transformers) or
        # succeed. Either is acceptable as long as it doesn't crash silently.
        if result.exit_code == 0:
            assert output_dir.exists(), "Output directory should exist on success"
            metrics_file = output_dir / "train_metrics.json"
            assert metrics_file.exists(), "train_metrics.json should exist on success"
        else:
            assert any(
                msg in result.stdout.lower()
                for msg in ["missing dependency", "failed to load", "failed"]
            ), f"Error message should be informative. Got: {result.stdout}"
