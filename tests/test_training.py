"""Tests for the training module and CLI train command."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


class TestFinetuneConfig:
    """FinetuneConfig can be constructed with sensible defaults."""

    def test_finetune_config_defaults(self):
        from deterministic_horizon.training.finetune import FinetuneConfig

        cfg = FinetuneConfig()
        assert cfg.model_name == "meta-llama/Llama-3.3-8B-Instruct"
        assert cfg.lora_r == 16
        assert cfg.num_epochs == 3
        assert cfg.batch_size == 4

    def test_finetune_config_custom(self):
        from deterministic_horizon.training.finetune import FinetuneConfig

        cfg = FinetuneConfig(model_name="test-model", lora_r=8, num_epochs=1)
        assert cfg.model_name == "test-model"
        assert cfg.lora_r == 8


class TestFinetuneDataset:
    """FinetuneDataset can be constructed and queried."""

    def test_dataset_length(self):
        from deterministic_horizon.training.finetune import FinetuneDataset

        data = [
            {
                "task_type": "permutation",
                "initial_state": [1, 2, 3, 4],
                "target_state": [4, 3, 2, 1],
                "optimal_trace": [("swap 0 3", [4, 2, 3, 1])],
                "depth": 1,
            }
        ]
        import transformers
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            "hf-internal-testing/llama-tokenizer"
        )
        dataset = FinetuneDataset(data, tokenizer, max_length=128)
        assert len(dataset) == 1


class TestFinetuneDataPreparation:
    """Data preparation utility works correctly."""

    def test_prepare_dataset_with_valid_instances(self):
        from deterministic_horizon.training.finetune import prepare_finetune_dataset

        with tempfile.TemporaryDirectory() as tmp:
            instances_path = Path(tmp) / "instances.json"
            train_path = Path(tmp) / "train.json"
            val_path = Path(tmp) / "val.json"

            # Create sample instances with valid optimal solutions
            instances = [
                {
                    "initial_state": [1, 2, 3],
                    "target_state": [3, 2, 1],
                    "optimal_solution": ["swap 0 2"],
                    "intermediate_states": [[3, 2, 1]],
                    "depth": 1,
                    "task_type": "permutation",
                },
                {
                    "initial_state": [1, 2, 3, 4],
                    "target_state": [4, 3, 2, 1],
                    "optimal_solution": ["swap 0 3", "swap 1 2"],
                    "intermediate_states": [[4, 2, 3, 1], [4, 3, 2, 1]],
                    "depth": 2,
                    "task_type": "permutation",
                },
                # Invalid: no optimal_solution
                {
                    "initial_state": [1, 2, 3],
                    "target_state": [3, 2, 1],
                    "depth": 5,
                    "task_type": "permutation",
                },
            ]

            instances_path.write_text(json.dumps(instances))

            n_train, n_val = prepare_finetune_dataset(
                instances_path,
                train_path,
                val_path,
                num_train=1,
                num_val=1,
                seed=42,
            )

            assert n_train == 1
            assert n_val == 1

            train_data = json.loads(train_path.read_text())
            val_data = json.loads(val_path.read_text())
            assert len(train_data) == 1
            assert len(val_data) == 1


@pytest.mark.slow
class TestCLITrainCommand:
    """CLI train command handles config loading and error paths."""

    def test_train_missing_config(self):
        from typer.testing import CliRunner
        from deterministic_horizon.cli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["train", "--config", "/nonexistent/config.yaml"],
        )
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower()

    def test_train_config_loads(self):
        """Verify that the existing config file is valid YAML and loads correctly."""
        import yaml
        from deterministic_horizon.training.finetune import FinetuneConfig

        config_path = Path("configs/finetune.yaml")
        if not config_path.exists():
            pytest.skip("configs/finetune.yaml not found")

        with open(config_path) as f:
            cfg_dict = yaml.safe_load(f)

        cfg = FinetuneConfig(
            model_name=cfg_dict.get("model_name"),
            lora_r=cfg_dict.get("lora_r"),
            lora_alpha=cfg_dict.get("lora_alpha"),
        )
        assert cfg.model_name == "meta-llama/Llama-3.3-8B-Instruct"
        assert cfg.lora_r == 16
        assert cfg.lora_alpha == 32
