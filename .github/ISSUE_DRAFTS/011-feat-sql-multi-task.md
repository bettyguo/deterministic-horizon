---
title: "[feat] SQL-Multi task: depth = JOIN/CTE chain length"
labels:
  - enhancement
  - help-wanted
  - new-task
milestone: "v1.2.0"
---

## Context

Text-to-SQL is one of the highest-traffic agent workloads in production and a natural fit for the Deterministic Horizon framework: the "depth" of a SQL query is roughly the number of joins and CTEs a planner has to track to produce a correct query. We expect the horizon prediction to hold cleanly, and a SQL-Multi task would substantially broaden the paper's empirical surface.

## What needs to happen

1. Add `src/deterministic_horizon/tasks/sql_multi.py` implementing `BaseTask`.
2. Generate synthetic instances by sampling a star-schema and a target tuple, then constructing the unique SQL query (via a planner) needed to retrieve it. `optimal_depth` is the number of joins in the canonical plan.
3. Operators are SQL clauses: `add_join`, `add_filter`, `add_groupby`, `add_having`, `add_subquery`. The C3 tool is a SQL executor against the underlying database.
4. Add `configs/task/sql_multi.yaml` with the schema parameters.
5. Add 100 sample instances under `data/sample/sql_multi.json`.

## Acceptance criteria

- [ ] `dh generate --task sql-multi --output data/sql.json` works.
- [ ] `python examples/demo.py` (or a sibling SQL-specific demo) reproduces a horizon estimate for the synthetic distribution.
- [ ] Unit tests under `tests/test_tasks_sql.py` cover the operator semantics and the BFS oracle.

## Hints

- Use SQLite in-memory for the C3 tool — zero external setup.
- The schema generator can borrow heavily from the BIRD / Spider patterns.
- "Depth = joins + CTEs" is the simple metric; if you want a more faithful measure, count *non-trivial* state transitions only (skip same-table re-joins).
