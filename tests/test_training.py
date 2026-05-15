"""Tests for the fine-tuning pipeline (CLI + Python API)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from deterministic_horizon.training.finetune import (
    FinetuneConfig,
    FinetuneTrainer,
    create_synthetic_data,
)


@pytest.fixture
def synthetic_train_data():
    """Create 16-sample synthetic training set."""
    return [
        {
            "task_type": "permutation",
            "initial_state": list(range(d)),
            "target_state": list(reversed(range(d))),
            "optimal_trace": [
                (f"swap({i},{d-1-i})", list(range(d)))
                for i in range(d // 2)
            ],
            "depth": d,
        }
        for d in [3, 4, 5, 6, 7]
        for _ in range(4)
    ][:16]


@pytest.fixture
def synthetic_val_data(synthetic_train_data):
    """4-sample validation set."""
    return synthetic_train_data[:4]


class TestFinetuneConfig:
    """Tests for FinetuneConfig dataclass."""

    def test_default_config(self):
        cfg = FinetuneConfig()
        assert cfg.model_name == "meta-llama/Llama-3.3-8B-Instruct"
        assert cfg.num_epochs == 3
        assert cfg.batch_size == 4
        assert cfg.lora_r == 16

    def test_custom_config(self):
        cfg = FinetuneConfig(
            model_name="sshleifer/tiny-gpt2",
            num_epochs=1,
            batch_size=2,
            output_dir="/tmp/test",
        )
        assert cfg.model_name == "sshleifer/tiny-gpt2"
        assert cfg.output_dir == "/tmp/test"

    def test_output_dir_from_config(self):
        cfg = FinetuneConfig(output_dir="custom/path")
        assert cfg.output_dir == "custom/path"


class TestTrainerSetup:
    """Tests for trainer initialization (requires torch)."""

    @pytest.mark.slow
    def test_trainer_setup_tiny_model(self, tmp_path):
        """Smoke test: can we set up a trainer with a tiny model?"""
        torch = pytest.importorskip("torch")
        transformers = pytest.importorskip("transformers")

        cfg = FinetuneConfig(
            model_name="sshleifer/tiny-gpt2",
            output_dir=str(tmp_path),
            batch_size=1,
            num_epochs=1,
            lora_r=2,
            lora_alpha=4,
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
        )

        trainer = FinetuneTrainer(cfg)
        trainer.setup()

        assert trainer.model is not None
        assert trainer.tokenizer is not None


class TestTrainingLoop:
    """End-to-end training loop tests."""

    @pytest.mark.slow
    def test_training_smoke(self, tmp_path, synthetic_train_data, synthetic_val_data):
        """Train for 3 steps on synthetic data and verify metrics."""
        torch = pytest.importorskip("torch")

        cfg = FinetuneConfig(
            model_name="sshleifer/tiny-gpt2",
            output_dir=str(tmp_path),
            num_epochs=1,
            batch_size=2,
            gradient_accumulation_steps=1,
            learning_rate=1e-4,
            max_seq_length=128,
            lora_r=2,
            lora_alpha=4,
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
        )

        trainer = FinetuneTrainer(cfg)
        trainer.setup()

        metrics = trainer.train(synthetic_train_data, synthetic_val_data)

        assert "train_loss" in metrics
        assert "train_runtime" in metrics
        assert metrics["train_loss"] is not None

    def test_empty_data_handling(self, tmp_path):
        """Empty data should be handled gracefully."""
        torch = pytest.importorskip("torch")

        cfg = FinetuneConfig(
            model_name="sshleifer/tiny-gpt2",
            output_dir=str(tmp_path),
            batch_size=1,
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
        )

        trainer = FinetuneTrainer(cfg)
        trainer.setup()

        # Empty data shouldn't crash during dataset creation
        from deterministic_horizon.training.finetune import FinetuneDataset

        dataset = FinetuneDataset([], trainer.tokenizer, max_length=128)
        assert len(dataset) == 0


class TestCLITrain:
    """Tests for the train CLI command."""

    def test_train_missing_config(self):
        """Missing config should fail with friendly message."""
        from typer.testing import CliRunner
        from deterministic_horizon.cli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["train", "--config", "nonexistent.yaml", "--output-dir", "/tmp/test"],
        )
        # Uses defaults since config doesn't exist (yellow warning)
        # But should fail on missing data files
        assert result.exit_code != 0

    def test_train_dry_run(self, tmp_path, synthetic_train_data, synthetic_val_data):
        """Dry run should validate config without training."""
        # Create temp data files
        train_file = tmp_path / "train.json"
        val_file = tmp_path / "val.json"
        train_file.write_text(json.dumps(synthetic_train_data))
        val_file.write_text(json.dumps(synthetic_val_data))

        from typer.testing import CliRunner
        from deterministic_horizon.cli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "train",
                "--output-dir", str(tmp_path / "checkpoints"),
                "--train-file", str(train_file),
                "--val-file", str(val_file),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Config validated" in result.stdout

    def test_train_missing_data_file(self, tmp_path):
        """Missing data file should produce friendly error."""
        from typer.testing import CliRunner
        from deterministic_horizon.cli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "train",
                "--output-dir", str(tmp_path),
                "--train-file", str(tmp_path / "nonexistent.json"),
                "--val-file", str(tmp_path / "nonexistent.json"),
            ],
        )
        assert result.exit_code == 1
