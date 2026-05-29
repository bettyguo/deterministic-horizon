"""Unit tests for tasks."""

from __future__ import annotations

import pytest
from deterministic_horizon import PermutationTask, generate_instances


def test_permutation_apply_operator_swap():
    task = PermutationTask(n_elements=4, seed=0)
    state = [0, 1, 2, 3]
    assert task.apply_operator(state, "swap_01") == [1, 0, 2, 3]
    assert task.apply_operator(state, "rotate_left") == [1, 2, 3, 0]
    assert task.apply_operator(state, "rotate_right") == [3, 0, 1, 2]


def test_permutation_bfs_returns_solution():
    task = PermutationTask(n_elements=4, seed=0)
    sol = task.bfs_solve([0, 1, 2, 3], [1, 0, 2, 3], max_depth=5)
    assert sol is not None
    ops, _ = sol
    assert ops == ["swap_01"]


def test_generate_instance_round_trip():
    task = PermutationTask(n_elements=6, seed=42)
    inst = task.generate_instance(target_depth=8)
    # Replaying the operator sequence on the initial state must yield the target.
    state = list(inst.initial_state)
    for op in inst.optimal_solution:
        state = task.apply_operator(state, op)
    assert task.state_equal(state, inst.target_state)
    assert inst.optimal_depth == 8


def test_generate_instances_helper():
    instances = generate_instances("permutation", n_instances=20, depth_range=(4, 12), seed=7)
    assert len(instances) > 0
    depths = {i.optimal_depth for i in instances}
    assert depths <= {4, 5, 6, 7, 8, 9, 10, 11, 12}


def test_unknown_task_raises():
    with pytest.raises(ValueError, match="Unknown task"):
        generate_instances("does-not-exist", n_instances=2)
