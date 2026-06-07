---
phase: 1
title: Academic Trace Contract
status: completed
priority: P2
effort: 1.5h
dependencies: []
---

# Phase 1: Academic Trace Contract

## Overview

Extend the canonical trace contract without removing existing trace columns. Add academic metadata for priority rules, selection keys, generated/skipped children, and support the `linear_conflict` heuristic in the canonical core.

## Implementation Steps

1. Extend `add_trace()` with optional fields while keeping the existing call pattern backward compatible.
2. Update BFS, DFS, UCS, Greedy, A*, IDS, IDA*, hill climbing, local beam, and simulated annealing to pass algorithm-specific priority and decision details.
3. Port `linear_conflict` from the package heuristic module into `eight_puzzle_search_app.py`.
4. Add `linear_conflict` to `get_heuristic()` aliases and any UI/doc lists that expose canonical heuristics.

## Success Criteria

- [x] Existing trace columns remain available.
- [x] New trace columns exist for every algorithm when trace is enabled.
- [x] A*/UCS/Greedy selection keys reflect f/g/h respectively.
- [x] IDA* trace includes threshold context and SA trace includes temperature/acceptance context.
- [x] `linear_conflict` is selectable and ordered above Manhattan on applicable states.
