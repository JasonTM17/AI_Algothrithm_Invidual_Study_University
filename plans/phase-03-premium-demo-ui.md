---
phase: 3
title: Premium Demo UI
status: completed
priority: P1
effort: 3h
dependencies:
  - 1
  - 2
---

# Phase 3: Premium Demo UI

## Overview

Refine the Streamlit interface into a compact, polished academic lab optimized
for live demo on desktop and mobile.

## Requirements

- Functional: result tabs become Summary, Trace, Heuristics, Experiment, Report.
- Functional: show status chips, trace story, heuristic inspector, and
  experiment table.
- Non-functional: no horizontal scroll on mobile; first viewport keeps Start
  board and Run CTA visible.
- Accessibility: labels remain visible and pass/fail states include text.

## Architecture

Keep Streamlit as the only frontend. Add small HTML helpers for chips and
section shells, use existing `st.dataframe`, `st.tabs`, and `st.download_button`
for stable rendering, and avoid new frontend dependencies.

## Related Code Files

- Modify: `streamlit_eight_puzzle_app.py`

## Implementation Steps

1. Extend localization keys for Heuristics, Experiment, Trace Story, and status
   chips.
2. Add CSS for compact panels, status chips, experiment tables, and mobile
   spacing.
3. Add Heuristics tab rendering `explain_heuristic(...)`.
4. Add Experiment tab rendering `run_experiment_suite(...)`.
5. Move academic context below results and keep first viewport action-focused.

## Success Criteria

- [ ] Desktop 1280x720 shows board and run controls without overlap.
- [ ] Mobile 390x844 has no horizontal scroll and a visible Run CTA early.
- [ ] All result tabs render after A* + Linear Conflict.
