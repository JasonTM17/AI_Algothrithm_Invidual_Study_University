---
phase: 2
title: Algorithm Hardening
status: completed
priority: P2
effort: 1h
dependencies:
  - 1
---

# Phase 2: Algorithm Hardening

## Overview

Reduce trace overhead in priority-search algorithms and add regression coverage for optimality, path validity, unsolvable handling, and trace-disabled runs.

## Requirements
- Functional: Existing algorithms keep their public behavior and result fields.
- Non-functional: UCS/A*/Greedy should not sort the entire frontier when trace output is disabled.

## Architecture
Preserve `run_algorithm()` as the public engine API. Add local helper tests rather than a new test framework dependency.

## Related Code Files
- Modify: `eight_puzzle_search_app.py`
- Create: `tests/test_search_behavior.py`

## Implementation Steps

1. Guard priority-search frontier preview creation behind the trace row limit.
2. Add tests for BFS/UCS/A*/IDA*/Greedy path validity.
3. Add heuristic and unsolvable-state regression tests.
4. Keep behavior-compatible result schema.

## Success Criteria

- [x] `max_trace_rows=0` avoids frontier sorting and does not crash.
- [x] A* matches BFS cost on shallow states.
- [x] Unsolvable states return without expansion.
