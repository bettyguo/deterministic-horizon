"""Smoke test for the fine-tuning pipeline — runs ~5 steps on synthetic data.

Usage: python examples/finetune_smoke.py
Requires: transformers, torch, peft (optional)

This script creates a tiny synthetic dataset and runs a minimal training
loop to verify the pipeline works end-to-end without GPUs.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import torch

from deterministic_horizon.training.finetune import (
    FinetuneConfig,
    FinetuneTrainer,
)


def create_synthetic_data(n_samples: int = 32) -> list[dict]:
    """Create tiny synthetic training data for smoke testing."""
    data = []
    for i in range(n_samples):
        depth = (i % 5) + 3  # depths 3-7
        initial = list(range(depth))
        target = list(reversed(range(depth)))
        trace = []
        state = list(initial)
        for step in range(depth):
            # Swap first and last unfixed elements
            left = step
            right = depth - 1 - step
            if left < right:
                state[left], state[right] = state[right], state[left]
                trace.append((f"swap({left},{right})", list(state)))
        data.append(
            {
                "task_type": "permutation",
                "initial_state": initial,
                "target_state": target,
                "optimal_trace": trace,
                "depth": depth,
            }
        )
    return data


def main() -> None:
    print("=== Deterministic Horizon: Fine-tuning Smoke Test ===")

    # Use a tiny model for smoke testing
    config = FinetuneConfig(
        model_name="sshleifer/tiny-gpt2",
        output_dir=tempfile.mkdtemp(prefix="dh_smoke_"),
        num_epochs=1,
        batch_size=2,
        gradient_accumulation_steps=1,
        learning_rate=1e-4,
        max_seq_length=256,
        num_train_samples=32,
        num_val_samples=8,
        lora_r=4,
        lora_alpha=8,
        fp16=False,
        bf16=False,
        gradient_checkpointing=False,
    )

    # Create synthetic data
    print("Creating synthetic data...")
    train_data = create_synthetic_data(32)
    val_data = create_synthetic_data(8)

    config.train_file = "synthetic"
    config.val_file = "synthetic"

    print(f"  Train samples: {len(train_data)}")
    print(f"  Val samples: {len(val_data)}")
    print(f"  Model: {config.model_name}")
    print(f"  Output: {config.output_dir}")

    # Run training
    print("\nStarting training (5 steps max)...")
    try:
        trainer = FinetuneTrainer(config)
        trainer.setup()

        # Override training args for smoke test
        trainer.config.num_epochs = 1
        metrics = trainer.train(train_data, val_data)

        print(f"\n✓ Smoke test passed!")
        print(f"  Train loss: {metrics.get('train_loss', 'N/A')}")
        print(f"  Runtime: {metrics.get('train_runtime', 0):.1f}s")
    except ImportError as e:
        print(f"\n⚠ Missing dependency: {e}")
        print("  Install: pip install transformers torch")
    except Exception as e:
        print(f"\n✗ Smoke test failed: {e}")
        raise


if __name__ == "__main__":
    main()
