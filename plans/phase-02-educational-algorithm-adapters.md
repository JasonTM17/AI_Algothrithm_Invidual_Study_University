---
phase: 2
title: Educational Algorithm Adapters
status: completed
priority: P1
effort: 4h
dependencies:
  - 1
---

# Phase 2: Educational Algorithm Adapters

## Overview

Implement canonical `SearchResult` adapters for the algorithms that are missing from the main app. Standard solvers remain exact; non-standard 8-puzzle algorithms run bounded educational models against the selected state.

## Requirements
- Functional: implement AND-OR, no-observation, partially-observable, online LRTA*, CSP definition/propagation/path consistency/global constraints/backtracking/min-conflicts/constraint graph, minimax, alpha-beta, and expectimax.
- Functional: each adapter produces trace rows with Node, Frontier, Reached, Generated Children, Skipped States, Selection Key, and Decision/Note where meaningful.
- Non-functional: bounded runtime with existing `SearchConfig` limits; no new required dependencies.

## Architecture
Adapters live in `eight_puzzle_search_app.py` and return the same `SearchResult` dataclass used by existing algorithms. They may delegate to shared helpers but must not make `8_puzzle_ai/` the canonical path.

## Related Code Files
- Modify: `eight_puzzle_search_app.py`
- Modify: `tests/test_search_behavior.py`

## Implementation Steps

1. Add complex-environment adapters with belief/online/nondeterministic trace semantics.
2. Add CSP educational adapters and bounded CSP backtracking/min-conflicts demos.
3. Add adversarial/stochastic depth-limited game-tree adapters.
4. Wire adapters into `run_algorithm`.
5. Add deterministic tests that every missing algorithm returns a canonical result without keyword/trace failures.

## Success Criteria

- [ ] Every missing algorithm runs through `run_algorithm`.
- [ ] Simulated algorithms clearly state they are educational extensions, not canonical solvers.
- [ ] Trace columns are complete for every algorithm.
