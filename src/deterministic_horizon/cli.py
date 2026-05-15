"""Command-line interface for Deterministic Horizon experiments."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from deterministic_horizon.config import load_config, save_config, Config
from deterministic_horizon.tasks import generate_instances, load_task, TASK_REGISTRY
from deterministic_horizon.models import load_model, MODEL_REGISTRY
from deterministic_horizon.metrics import (
    accuracy_by_depth,
    estimate_horizon,
    compute_ssj,
    compute_sfe,
)

app = typer.Typer(
    name="deterministic-horizon",
    help="Investigating boundaries of inference-time compute in transformers",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    task: str = typer.Option("permutation", help="Task type"),
    n_instances: int = typer.Option(1000, help="Number of instances"),
    min_depth: int = typer.Option(5, help="Minimum reasoning depth"),
    max_depth: int = typer.Option(50, help="Maximum reasoning depth"),
    depth_step: int = typer.Option(5, help="Step between depths"),
    seed: int = typer.Option(42, help="Random seed"),
    output: Path = typer.Option(..., help="Output file path"),
) -> None:
    """Generate task instances for evaluation."""
    console.print(f"[bold blue]Generating {n_instances} {task} instances...[/]")
    
    if task not in TASK_REGISTRY:
        console.print(f"[red]Unknown task: {task}[/]")
        console.print(f"Available: {', '.join(TASK_REGISTRY.keys())}")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Generating instances...", total=None)
        
        instances = generate_instances(
            task=task,
            n_instances=n_instances,
            depth_range=(min_depth, max_depth),
            seed=seed,
        )
    
    # Save to file
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump([inst.to_dict() for inst in instances], f, indent=2)
    
    console.print(f"[green]✓ Generated {len(instances)} instances to {output}[/]")
    
    # Show depth distribution
    depth_counts = {}
    for inst in instances:
        d = inst.optimal_depth
        depth_counts[d] = depth_counts.get(d, 0) + 1
    
    table = Table(title="Depth Distribution")
    table.add_column("Depth", style="cyan")
    table.add_column("Count", style="green")
    
    for depth in sorted(depth_counts.keys()):
        table.add_row(str(depth), str(depth_counts[depth]))
    
    console.print(table)


@app.command()
def evaluate(
    model: str = typer.Option(..., help="Model name (e.g., gpt-4o)"),
    instances: Path = typer.Option(..., help="Path to instances JSON"),
    conditions: str = typer.Option("C1,C3", help="Comma-separated conditions"),
    output: Path = typer.Option(..., help="Output file path"),
    batch_size: int = typer.Option(50, help="Batch size"),
    max_instances: Optional[int] = typer.Option(None, help="Max instances to evaluate"),
) -> None:
    """Evaluate a model on task instances."""
    from deterministic_horizon.tasks.base import TaskInstance
    
    console.print(f"[bold blue]Evaluating {model} on {instances}...[/]")
    
    # Load instances
    with open(instances) as f:
        instance_data = json.load(f)
    
    task_instances = [TaskInstance.from_dict(d) for d in instance_data]
    
    if max_instances:
        task_instances = task_instances[:max_instances]
    
    # Parse conditions
    condition_list = [c.strip() for c in conditions.split(",")]
    
    # Load model
    try:
        model_obj = load_model(model, temperature=0.0)
    except Exception as e:
        console.print(f"[red]Failed to load model: {e}[/]")
        raise typer.Exit(1)
    
    # Load task for evaluation
    task_name = task_instances[0].task_name if task_instances else "permutation"
    task_obj = load_task(task_name)
    
    results = []
    
    with Progress(console=console) as progress:
        total = len(task_instances) * len(condition_list)
        task_progress = progress.add_task("Evaluating...", total=total)
        
        for condition in condition_list:
            for instance in task_instances:
                try:
                    # Format prompt for condition
                    prompt, system_prompt = task_obj.format_prompt(
                        instance.initial_state,
                        instance.target_state,
                        condition,
                    )
                    
                    # Generate response
                    if condition == "C3":
                        # Tool-integrated
                        tools = task_obj.get_tool_definitions()
                        response = model_obj.generate_with_tools(
                            prompt, tools, system_prompt
                        )
                    else:
                        response = model_obj.generate(prompt, system_prompt)
                    
                    # Evaluate
                    result = task_obj.evaluate(instance, response.content)
                    result.condition = condition
                    result.model = model
                    result.total_tokens = response.total_tokens
                    result.latency_ms = response.latency_ms
                    result.tool_calls = response.tool_calls
                    
                    results.append(result.to_dict())
                    
                except Exception as e:
                    console.print(f"[yellow]Warning: {instance.instance_id}: {e}[/]")
                    results.append({
                        "instance_id": instance.instance_id,
                        "condition": condition,
                        "model": model,
                        "correct": False,
                        "error": str(e),
                    })
                
                progress.advance(task_progress)
    
    # Save results
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    
    console.print(f"[green]✓ Saved {len(results)} results to {output}[/]")
    
    # Show summary
    for condition in condition_list:
        cond_results = [r for r in results if r.get("condition") == condition]
        correct = sum(1 for r in cond_results if r.get("correct", False))
        total = len(cond_results)
        acc = correct / total * 100 if total > 0 else 0
        console.print(f"  {condition}: {acc:.1f}% ({correct}/{total})")


@app.command()
def analyze(
    results: Path = typer.Option(..., help="Path to results JSON"),
    output: Path = typer.Option("analysis/", help="Output directory"),
    generate_figures: bool = typer.Option(True, help="Generate figures"),
) -> None:
    """Analyze results and generate figures."""
    console.print(f"[bold blue]Analyzing results from {results}...[/]")
    
    # Load results
    with open(results) as f:
        result_data = json.load(f)
    
    output.mkdir(parents=True, exist_ok=True)
    
    # Compute metrics
    metrics = {}
    
    # Accuracy by depth
    acc_depth = accuracy_by_depth(result_data, "optimal_depth", "correct")
    metrics["accuracy_by_depth"] = acc_depth
    
    # Estimate horizon
    horizon = estimate_horizon(result_data, threshold=0.5)
    metrics["horizon"] = horizon
    
    console.print(f"\n[bold]Deterministic Horizon (d*):[/]")
    console.print(f"  d* = {horizon['d_star']:.1f}")
    if "d_star_ci_low" in horizon:
        console.print(f"  95% CI: [{horizon['d_star_ci_low']:.1f}, {horizon['d_star_ci_high']:.1f}]")
    
    # Save metrics
    metrics_path = output / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, default=float)
    
    console.print(f"[green]✓ Saved metrics to {metrics_path}[/]")
    
    # Generate figures if requested
    if generate_figures:
        try:
            from deterministic_horizon.analysis import generate_figures as gen_figs
            gen_figs(result_data, output)
            console.print(f"[green]✓ Generated figures in {output}[/]")
        except ImportError:
            console.print("[yellow]matplotlib not available, skipping figures[/]")
    
    # Print accuracy table
    table = Table(title="Accuracy by Depth")
    table.add_column("Depth", style="cyan")
    table.add_column("Accuracy", style="green")
    table.add_column("95% CI", style="yellow")
    table.add_column("N", style="dim")
    
    for depth in sorted(acc_depth.keys()):
        stats = acc_depth[depth]
        ci = f"[{stats['ci_low']:.2f}, {stats['ci_high']:.2f}]"
        table.add_row(
            str(depth),
            f"{stats['accuracy']:.2%}",
            ci,
            str(stats['n']),
        )
    
    console.print(table)


@app.command()
def train(
    config: Path = typer.Option("configs/finetune.yaml", help="Config file"),
    output_dir: Path = typer.Option("checkpoints/", help="Output directory"),
    train_file: Path = typer.Option(None, help="Path to training data JSON"),
    val_file: Path = typer.Option(None, help="Path to validation data JSON"),
    model_name: str = typer.Option(None, help="Model name (overrides config)"),
    num_epochs: int = typer.Option(None, help="Number of epochs (overrides config)"),
    dry_run: bool = typer.Option(False, help="Validate config without training"),
) -> None:
    """Fine-tune a model on optimal-length traces (C5 condition)."""
    from deterministic_horizon.training.finetune import (
        FinetuneConfig,
        run_finetuning,
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load base config (training-specific YAML or default)
    finetune_cfg = FinetuneConfig(output_dir=str(output_dir))

    if config.exists():
        try:
            import yaml
            with open(config) as f:
                cfg_data = yaml.safe_load(f)

            if cfg_data:
                ft_section = cfg_data.get("finetune", cfg_data)
                for key, value in ft_section.items():
                    if hasattr(finetune_cfg, key):
                        setattr(finetune_cfg, key, value)
        except Exception as e:
            console.print(f"[red]Error loading config {config}: {e}[/]")
            raise typer.Exit(1)
    else:
        console.print(f"[yellow]Config {config} not found, using defaults[/]")

    # CLI overrides
    if model_name:
        finetune_cfg.model_name = model_name
    if num_epochs is not None:
        finetune_cfg.num_epochs = num_epochs
    if train_file:
        finetune_cfg.train_file = str(train_file)
    if val_file:
        finetune_cfg.val_file = str(val_file)

    # Validate data files exist
    train_path = Path(finetune_cfg.train_file)
    val_path = Path(finetune_cfg.val_file)

    if not train_path.exists():
        console.print(f"[red]Training data not found: {train_path}[/]")
        console.print("[yellow]Generate data first: dh generate --task permutation --output[/]")
        raise typer.Exit(1)

    if not val_path.exists():
        console.print(f"[red]Validation data not found: {val_path}[/]")
        console.print("[yellow]Generate data first or specify --val-file[/]")
        raise typer.Exit(1)

    console.print(f"[bold blue]Fine-tuning Configuration[/]")
    console.print(f"  Model: {finetune_cfg.model_name}")
    console.print(f"  Output: {finetune_cfg.output_dir}")
    console.print(f"  Train data: {train_path} ({finetune_cfg.num_train_samples} samples)")
    console.print(f"  Val data: {val_path} ({finetune_cfg.num_val_samples} samples)")
    console.print(f"  LoRA: r={finetune_cfg.lora_r}, alpha={finetune_cfg.lora_alpha}")
    console.print(f"  Epochs: {finetune_cfg.num_epochs}, LR: {finetune_cfg.learning_rate}")

    if dry_run:
        console.print("[green]✓ Config validated (dry-run)[/]")
        return

    try:
        console.print("[bold blue]Starting fine-tuning...[/]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Training in progress...", total=None)
            results = run_finetuning(
                config=finetune_cfg,
                train_file=train_path,
                val_file=val_path,
            )

        # Write train_metrics.json
        metrics_path = output_dir / "train_metrics.json"
        metrics = {
            "model": finetune_cfg.model_name,
            "num_epochs": finetune_cfg.num_epochs,
            "learning_rate": finetune_cfg.learning_rate,
            "batch_size": finetune_cfg.batch_size,
            "train_loss": results.get("metrics", {}).get("train_loss"),
            "train_runtime_s": results.get("metrics", {}).get("train_runtime"),
            "train_samples": results.get("num_train_samples"),
            "val_samples": results.get("num_val_samples"),
            "output_dir": str(output_dir),
        }
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2, default=float)

        console.print(f"[green]✓ Training complete[/]")
        console.print(f"[green]✓ Checkpoint saved to {output_dir}[/]")
        console.print(f"[green]✓ Metrics saved to {metrics_path}[/]")

    except ImportError as e:
        console.print(f"[red]Missing dependency: {e}[/]")
        console.print("[yellow]Install with: pip install transformers torch peft[/]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Training failed: {e}[/]")
        raise typer.Exit(1)


@app.command()
def list_models() -> None:
    """List available models."""
    table = Table(title="Available Models")
    table.add_column("Model", style="cyan")
    table.add_column("Provider", style="green")
    
    for model_name, model_class in sorted(MODEL_REGISTRY.items()):
        provider = model_class.__name__.replace("Model", "")
        table.add_row(model_name, provider)
    
    console.print(table)


@app.command()
def list_tasks() -> None:
    """List available tasks."""
    table = Table(title="Available Tasks")
    table.add_column("Task", style="cyan")
    table.add_column("Description", style="green")
    
    descriptions = {
        "permutation": "Permutation puzzle (swap, rotate operations)",
        "fsa": "Finite State Automaton simulation",
        "arithmetic": "Multi-step arithmetic operations",
    }
    
    for task_name in sorted(TASK_REGISTRY.keys()):
        desc = descriptions.get(task_name, "")
        table.add_row(task_name, desc)
    
    console.print(table)


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
