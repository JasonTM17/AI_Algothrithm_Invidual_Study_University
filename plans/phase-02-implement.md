---
phase: 2
title: Implement
status: completed
effort: 3h
---

# Phase 2: Implement

## Overview

Implement the standalone Python module with search algorithms, trace collection, comparison helpers, and Jupyter UI/fallback display functions.

## Implementation Steps

1. Define constants, dataclasses, algorithm metadata, board formatting, heuristics, neighbors, solvability, and random start helpers.
2. Implement graph/tree searches: BFS, DFS, UCS, IDS, Greedy, A*, and IDA* with shared trace formatting where practical.
3. Implement local searches: Simple Hill Climbing, Steepest-Ascent, Stochastic Hill Climbing, Random-Restart Hill Climbing, and Local Beam Search.
4. Add public API functions: `run_algorithm`, `compare_algorithms`, `render_board`, `render_trace_table`, `launch_jupyter_app`, and `run_demo`.
5. Add CLI handling for `--self-test`, `--demo`, and optional start-state arguments.

## Success Criteria

- [ ] `eight_puzzle_search_app.py` exists and imports without optional Jupyter dependencies.
- [ ] All requested algorithms are selectable by canonical name and common aliases.
- [ ] Trace rows include `Step`, `Algorithm`, `Node`, `Action`, `Depth`, `g`, `h`, `f`, `Frontier`, `Reached`, and `Decision/Note`.
- [ ] Comparison output includes completeness/optimality notes and runtime/search metrics.
