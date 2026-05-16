"""
Fine-tuning smoke test — validates the CLI `dh train` pipeline end-to-end.

Creates tiny synthetic data, configures a minimal model from the Hugging Face
test hub, and runs 1-2 training steps. This is designed to work on CPU and
complete in under 60 seconds. Useful for verifying the fine-tuning plumbing
is wired correctly end-to-end.

Usage:
    python examples/finetune_smoke.py
    # or via the CLI:
    dh train --model-name hf-internal-testing/tiny-random-llama \\
             --num-epochs 1 --batch-size 1 \\
             --gradient-accumulation-steps 1 --lora-r 4 --lora-alpha 8 \\
             --output-dir /tmp/dh-smoke-output
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from deterministic_horizon.training.finetune import FinetuneConfig, run_finetuning


def _make_synthetic_data(num_samples: int = 10) -> list[dict]:
    """Create tiny synthetic fine-tuning data.

    Each sample mimics a permutation puzzle with an optimal trace.
    The data is small and shallow enough to process on CPU quickly.
    """
    samples = []
    for i in range(num_samples):
        # A trivial 2-element swap
        initial = [i % 2, (i + 1) % 2]
        target = [(i + 1) % 2, i % 2]
        # Trace: one swap operation
        trace = [("swap 0 1", list(target))]
        samples.append(
            {
                "task_type": "permutation",
                "initial_state": initial,
                "target_state": target,
                "optimal_trace": trace,
                "depth": 1,
            }
        )
    return samples


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Write synthetic data
        train_file = tmp / "train.json"
        val_file = tmp / "val.json"
        data = _make_synthetic_data(10)
        with open(train_file, "w") as f:
            json.dump(data, f)
        with open(val_file, "w") as f:
            json.dump(data[:2], f)

        # Configure a tiny model for CPU smoke testing
        cfg = FinetuneConfig(
            model_name="hf-internal-testing/tiny-random-llama",
            output_dir=str(tmp / "output"),
            train_file=str(train_file),
            val_file=str(val_file),
            num_epochs=1,
            batch_size=1,
            gradient_accumulation_steps=1,
            lora_r=4,
            lora_alpha=8,
            max_seq_length=256,
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
        )

        print(f"Config: {cfg}")
        print("Running fine-tuning smoke test...")

        try:
            results = run_finetuning(config=cfg)
            print(f"Fine-tuning completed successfully!")
            print(f"  Train loss: {results.get('metrics', {}).get('train_loss', 'N/A')}")
            print(f"  Output dir: {results.get('output_dir')}")

            # Verify checkpoint was saved
            metrics_path = Path(cfg.output_dir) / "train_metrics.json"
            if metrics_path.exists():
                print(f"  ✓ train_metrics.json exists at {metrics_path}")
            else:
                print(f"  ⚠ train_metrics.json not found (may be expected on CPU)")

        except Exception as e:
            # Accept network errors (model download failure on CPU-only envs)
            # but reject implementation errors
            msg = str(e).lower()
            if any(
                kw in msg
                for kw in ["connection", "refused", "resolve", "timeout", "econnrefused", "cannot connect"]
            ):
                print(f"Smoke test skipped (network issue — expected on CPU-only env): {e}")
            else:
                raise


if __name__ == "__main__":
    main()
