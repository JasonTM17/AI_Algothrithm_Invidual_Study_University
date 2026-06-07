---
phase: 3
title: UI Grouping And Theory
status: completed
priority: P2
effort: 2h
dependencies:
  - 1
  - 2
---

# Phase 3: UI Grouping And Theory

## Overview

Update Streamlit UI so the app visibly follows the six academic groups from the coursework spec and makes missing/non-standard algorithms understandable.

## Requirements
- Functional: add group-first algorithm selection.
- Functional: show theory/guarantee metadata for selected algorithms.
- Functional: keep first viewport focused on board, preset, algorithm, heuristic, and Run CTA.
- Non-functional: mobile-safe layout without horizontal overflow.

## Architecture
The UI should derive group options and algorithms from core registry helpers. It should not maintain a divergent hard-coded list.

## Related Code Files
- Modify: `streamlit_eight_puzzle_app.py`
- Modify: `README.md`

## Implementation Steps

1. Add group selectbox before algorithm selectbox in the sidebar/main control panel.
2. Add compact theory/limitation notes for selected algorithm in Summary/Trace sections.
3. Ensure benchmark defaults exclude heavy educational demos unless explicitly selected.
4. Update README with six-group algorithm table and canonical run command.

## Success Criteria

- [ ] UI exposes all six groups and all 27 algorithms.
- [ ] Non-standard algorithms display clear educational labels.
- [ ] Existing A* linear conflict demo remains the smooth default path.
