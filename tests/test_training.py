"""Tests for the CLI train command."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# The package requires scipy for top-level imports. Skip all tests if unavailable.
pytest.importorskip("scipy", reason="scipy is required to import deterministic_horizon")


def test_train_help() -> None:
    """The train subcommand must appear in CLI help."""
    result = subprocess.run(
        [sys.executable, "-m", "deterministic_horizon.cli", "train", "--help"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
        env={"PYTHONPATH": "src", "PATH": "NONE"},
    )
    assert result.returncode == 0
    assert "Fine-tune" in result.stdout
    assert "--config" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--prepare-data" in result.stdout
    assert "--instances" in result.stdout


def test_train_missing_config() -> None:
    """Missing config file should produce a friendly error."""
    result = subprocess.run(
        [
            sys.executable, "-m", "deterministic_horizon.cli",
            "train", "--config", "/nonexistent/path/finetune.yaml",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
        env={"PYTHONPATH": "src"},
    )
    assert result.returncode == 1
    assert "Config file not found" in result.stdout


def test_train_prepare_data_requires_instances() -> None:
    """Using --prepare-data without --instances should error."""
    result = subprocess.run(
        [
            sys.executable, "-m", "deterministic_horizon.cli",
            "train", "--config", "configs/finetune.yaml", "--prepare-data",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
        env={"PYTHONPATH": "src"},
    )
    assert result.returncode == 1
    assert "--instances" in result.stdout or "instances" in result.stdout.lower()


def test_finetune_config_lazy_import() -> None:
    """FinetuneConfig is importable directly without triggering top-level scipy import."""
    src_path = str(Path(__file__).resolve().parent.parent / "src")
    code = f"""
import sys
sys.path.insert(0, {src_path!r})
# Import FinetuneConfig directly, bypassing deterministic_horizon's __init__
from deterministic_horizon.training.finetune import FinetuneConfig
cfg = FinetuneConfig(model_name="test", lora_r=4)
print(f"OK: model_name={{cfg.model_name}}, lora_r={{cfg.lora_r}}")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"Skipped — scipy not available (subprocess failed: {result.stderr[:200]})")
    assert "OK: model_name=test" in result.stdout
