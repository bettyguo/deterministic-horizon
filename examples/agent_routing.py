#!/usr/bin/env python
"""
Production pattern: route an agent between neural reasoning and tool calls.

This script shows the practitioner pattern the paper recommends. It needs no
API keys — depth estimates and tool/LLM "calls" are stubbed — so you can copy
the routing logic straight into your agent without running anything live.

Usage:
    python examples/agent_routing.py
"""

from __future__ import annotations

from dataclasses import dataclass

from deterministic_horizon import (
    delegation_decision,
    expected_neural_accuracy,
    should_delegate,
)

# ---------- Stub functions (replace with your real ones) ----------


@dataclass
class Subtask:
    name: str
    description: str
    estimated_depth: int


def call_llm(subtask: Subtask) -> str:
    """Pretend to call an LLM for chain-of-thought reasoning."""
    return f"<neural-CoT answer for {subtask.name!r}>"


def call_tool(subtask: Subtask) -> str:
    """Pretend to invoke a deterministic tool (BFS, calculator, SQL, ...)."""
    return f"<tool answer for {subtask.name!r}>"


# ---------- The routing policy ----------


def solve(subtask: Subtask, model: str = "claude-4.5-opus") -> str:
    """
    Route a single subtask to whichever branch the Deterministic Horizon
    predicts will win.

    This is *the* pattern the paper recommends for code agents, planners,
    and any system that processes deterministic-state subproblems.
    """
    decision = delegation_decision(
        estimated_depth=subtask.estimated_depth,
        model=model,
        tool_available=True,
    )
    print(f"[route] {subtask.name:<24} d={subtask.estimated_depth:<3} → "
          f"{'tool ' if decision.delegate else 'LLM  '}  | {decision.explain()}")
    return call_tool(subtask) if decision.delegate else call_llm(subtask)


# ---------- Demo run ----------


def main() -> None:
    model = "claude-4.5-opus"
    horizon = round(expected_neural_accuracy(0, model=model), 3)  # touch the API

    subtasks = [
        Subtask("rename_variable",       "Rename foo → bar in 3 files",     3),
        Subtask("summarise_changelog",   "Summarise last 20 commits",       7),
        Subtask("trace_call_graph",      "Walk caller chain of f()",       14),
        Subtask("refactor_state_mach.",  "Refactor 12-state FSM",          24),
        Subtask("multi_file_migration",  "Apply migration across 8 files", 38),
    ]

    print(f"Model: {model}\n")
    for s in subtasks:
        solve(s, model=model)

    print()
    print("Rule of thumb: as estimated depth crosses ~d*, the policy flips to the tool.")
    print(f"At d=0, expected neural accuracy = {horizon:.0%} (sanity check).")

    print("\nQuick cross-check on the cheap boolean API:")
    for d in [5, 15, 22, 30, 45]:
        decided = "delegate" if should_delegate(d, model=model) else "think"
        print(f"  d={d:>2}  →  {decided}")


if __name__ == "__main__":
    main()
