---
phase: 3
title: Test
status: completed
effort: 1h
---

# Phase 3: Test

## Overview

Verify correctness, graceful failure modes, and user-facing table output.

## Implementation Steps

1. Run `python eight_puzzle_search_app.py --self-test`.
2. Run a demo comparison on a small solvable puzzle.
3. Compile the module to catch syntax issues.
4. Inspect generated trace/comparison columns.

## Success Criteria

- [ ] Goal state returns a zero-step solution.
- [ ] Easy states give matching optimal path lengths for BFS, UCS, IDS, and A*.
- [ ] Random states are solvable by construction.
- [ ] Unsolvable states are rejected without long search.
- [ ] Trace tables contain Node, Frontier, and Reached columns.
