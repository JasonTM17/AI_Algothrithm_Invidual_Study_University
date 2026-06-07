---
phase: 2
title: Heuristic Explainer
status: completed
priority: P1
effort: 2h
dependencies:
  - 1
---

# Phase 2: Heuristic Explainer

## Overview

Add an academic heuristic inspector and trace story layer so each run can
explain how h(n), f(n), and the selected trace row were produced.

## Requirements

- Functional: expose `explain_heuristic(...)` and `build_trace_story(...)`.
- Functional: include misplaced, Manhattan, and Linear Conflict totals plus
  per-tile contribution rows.
- Functional: list row/column linear conflicts for Linear Conflict.
- Non-functional: keep trace columns backward compatible.

## Architecture

The heuristic helper derives all values from the existing heuristic functions and
returns a plain dictionary for tests/UI/reporting. The trace story helper maps
existing trace rows into concise "why this node" explanations without changing
algorithm behavior.

## Related Code Files

- Modify: `eight_puzzle_search_app.py`
- Modify: `streamlit_eight_puzzle_app.py`
- Modify: `tests/test_search_behavior.py`

## Implementation Steps

1. Add tile-level Manhattan/misplaced contribution rows.
2. Add Linear Conflict pair detection for rows and columns.
3. Build an invariant explanation object with totals and ordering notes.
4. Add trace-story text using algorithm priority rules and selection keys.
5. Add tests for totals, conflict pairs, and representative algorithms.

## Success Criteria

- [ ] Inspector proves `linear_conflict >= manhattan >= misplaced` for the
      inspected state.
- [ ] Trace story has human-readable explanations for BFS, A*, IDA*, and SA.
- [ ] Existing trace table output remains unchanged.
