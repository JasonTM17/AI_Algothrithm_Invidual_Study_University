---
phase: 1
title: Experiment Layer
status: completed
priority: P1
effort: 2h
dependencies: []
---

# Phase 1: Experiment Layer

## Overview

Add a deterministic, small-scale experiment layer for comparing algorithms on
fixed demo presets without making the Streamlit app slow or unstable.

## Requirements

- Functional: expose `run_experiment_suite(...)` and
  `export_experiment_markdown(...)` in the core module.
- Functional: compare Found, Cost, Expanded, Generated, Runtime, Memory,
  Complete, Optimal, and Optimal Gap.
- Non-functional: use `max_trace_rows=0` by default for experiment runs.
- Compatibility: preserve `compare_algorithms(...)` and `SearchResult`.

## Architecture

The experiment helper runs selected algorithms across `DEMO_PRESETS`, captures a
baseline optimal cost from BFS/UCS/A*/IDA* where available, and returns a plain
dictionary containing stable rows plus metadata. Streamlit renders the rows
directly and can export the Markdown text.

## Related Code Files

- Modify: `eight_puzzle_search_app.py`
- Modify: `streamlit_eight_puzzle_app.py`
- Modify: `tests/test_search_behavior.py`

## Implementation Steps

1. Add default experiment algorithm/preset constants.
2. Implement `run_experiment_suite(...)` with defensive parsing and bounded
   config defaults.
3. Add optimal-gap calculation relative to the best optimal baseline found per
   preset.
4. Implement `export_experiment_markdown(...)`.
5. Add tests for deterministic output and unsolvable handling.

## Success Criteria

- [ ] Experiment helper returns stable rows for the fixed demo presets.
- [ ] Optimal Gap is numeric when a valid baseline exists and blank otherwise.
- [ ] Markdown export includes setup, rows, and an academic conclusion.
