---
phase: 3
title: Algorithm Correctness UX Guards
status: completed
priority: P1
effort: 3h
dependencies:
  - 2
---

# Phase 3: Algorithm Correctness UX Guards

## Overview

Add UI and core guardrails so users cannot misinterpret educational algorithms
as standard 8-puzzle solvers, and so solver runs remain algorithmically correct.

## Implementation Steps

1. Add/verify a shared `algorithm_run_mode()` helper returning:
   `standard_solver`, `educational_complex`, `educational_csp`,
   `educational_adversarial`, plus Vietnamese/English explanation.
2. In the UI, show mode chips:
   - `Solver chuẩn` for BFS, DFS, UCS, IDS, Greedy, A*, IDA*, local search.
   - `Mô phỏng học thuật` for Complex/CSP/Adversarial groups.
3. Add pre-run validation panel:
   - state has digits 0..8 exactly once;
   - solvability known;
   - goal is fixed for standard solvers;
   - partial goal is valid when selected.
4. Add result certificate detail by algorithm family:
   - BFS/UCS/A*/IDA*: optimality condition.
   - DFS/Greedy/local search: limitation warning.
   - Complex/CSP/Adversarial: model-scope warning.
5. Protect h(n) semantics:
   - `DEFAULT_HEURISTICS` remains `["misplaced", "manhattan"]`;
   - non-heuristic algorithms display h(n) only for explanation, not priority.
6. Add tests asserting all 27 algorithms still run through `run_algorithm()` and
   preserve existing trace columns.

## Success Criteria

- [ ] BFS/UCS/A*/IDA* still match optimal path cost on shallow states.
- [ ] Unsolvable input stops before expansion with `expanded = 0`.
- [ ] Every algorithm displays a Vietnamese PEAS card and a model-scope note.
- [ ] Standard solvers are not mixed with educational models in benchmark
      conclusions.
- [ ] No algorithm receives UI params it does not support in `8_puzzle_ai/app.py`.
