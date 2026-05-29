"""Command-line interface for Deterministic Horizon experiments."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
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
    prepare_data: bool = typer.Option(
        False, "--prepare-data", help="Prepare dataset from generated instances before training"
    ),
    instances: Optional[Path] = typer.Option(
        None, "--instances", help="Path to generated instances JSON (required with --prepare-data)"
    ),
) -> None:
    """Fine-tune a model on optimal-length traces (C5 condition).

    Loads a YAML configuration, runs LoRA fine-tuning on the C5 condition
    dataset, and saves the trained checkpoint plus metrics.
    """
    # Validate config path
    config_path = Path(config)
    if not config_path.exists():
        console.print(f"[red]Error: Config file not found: {config_path}[/]")
        console.print("Create one from the template at configs/finetune.yaml")
        raise typer.Exit(1)

    # Load YAML config into FinetuneConfig
    console.print(f"[bold blue]Loading config from {config_path}...[/]")
    with open(config_path) as f:
        raw_config = yaml.safe_load(f) or {}

    from deterministic_horizon.training.finetune import FinetuneConfig, run_finetuning

    ft_config = FinetuneConfig(
        model_name=raw_config.get("model_name", "meta-llama/Llama-3.3-8B-Instruct"),
        output_dir=str(output_dir),
        lora_r=raw_config.get("lora_r", 16),
        lora_alpha=raw_config.get("lora_alpha", 32),
        lora_dropout=raw_config.get("lora_dropout", 0.05),
        lora_target_modules=raw_config.get(
            "lora_target_modules",
            ["q_proj", "k_proj", "v_proj", "o_proj"],
        ),
        num_epochs=raw_config.get("num_epochs", 3),
        batch_size=raw_config.get("batch_size", 4),
        gradient_accumulation_steps=raw_config.get("gradient_accumulation_steps", 4),
        learning_rate=raw_config.get("learning_rate", 2e-5),
        warmup_ratio=raw_config.get("warmup_ratio", 0.03),
        max_seq_length=raw_config.get("max_seq_length", 2048),
        weight_decay=raw_config.get("weight_decay", 0.01),
        train_file=raw_config.get("train_file", "data/finetune_train.json"),
        val_file=raw_config.get("val_file", "data/finetune_val.json"),
        num_train_samples=raw_config.get("num_train_samples", 5000),
        num_val_samples=raw_config.get("num_val_samples", 500),
        seed=raw_config.get("seed", 42),
        fp16=raw_config.get("fp16", True),
        bf16=raw_config.get("bf16", False),
        gradient_checkpointing=raw_config.get("gradient_checkpointing", True),
    )

    # Optionally prepare dataset
    if prepare_data:
        if instances is None:
            console.print(
                "[red]Error: --instances is required when --prepare-data is set[/]"
            )
            raise typer.Exit(1)
        instances_path = Path(instances)
        if not instances_path.exists():
            console.print(f"[red]Error: Instances file not found: {instances_path}[/]")
            raise typer.Exit(1)

        console.print("[bold blue]Preparing fine-tuning dataset...[/]")
        from deterministic_horizon.training.finetune import prepare_finetune_dataset

        train_file = Path(ft_config.train_file)
        val_file = Path(ft_config.val_file)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Generating dataset...", total=None)
            n_train, n_val = prepare_finetune_dataset(
                instances_file=instances_path,
                output_train=train_file,
                output_val=val_file,
                num_train=ft_config.num_train_samples,
                num_val=ft_config.num_val_samples,
                seed=ft_config.seed,
            )
        console.print(
            f"[green]✓ Prepared {n_train} training + {n_val} validation samples[/]"
        )

    # Run fine-tuning
    console.print(
        f"[bold blue]Starting fine-tuning on {ft_config.model_name}...[/]"
    )
    console.print(
        f"  Output directory: {output_dir.resolve()}"
    )

    # Note: run_finetuning internally handles training progress via HF Trainer
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fine-tuning (see HF logs for step details)...", total=None)
        try:
            results = run_finetuning(config=ft_config)
        except Exception as e:
            console.print(f"[red]Fine-tuning failed: {e}[/]")
            raise typer.Exit(1)

    # Report results
    metrics = results.get("metrics", {})
    console.print(f"[green]✓ Fine-tuning complete[/]")
    console.print(f"  Train loss: {metrics.get('train_loss', 'N/A'):.4f}")
    console.print(f"  Runtime: {metrics.get('train_runtime', 0):.1f}s")
    console.print(f"  Samples/sec: {metrics.get('train_samples_per_second', 0):.2f}")
    console.print(f"  Output: {output_dir.resolve()}")


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
