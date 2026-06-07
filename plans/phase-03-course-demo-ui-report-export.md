---
phase: 3
title: Course Demo UI & Report Export
status: completed
priority: P2
effort: 2h
dependencies:
  - 1
  - 2
---

# Phase 3: Course Demo UI & Report Export

## Overview

Restructure the Streamlit result area for classroom/demo use with tabs, deterministic presets, benchmark output, and Markdown download.

## Implementation Steps

1. Add heuristic option `linear_conflict` and deterministic demo presets: `easy_2`, `medium_10`, `hard_20`, `unsolvable_demo`.
2. Keep the first viewport compact on desktop/mobile: start board and run CTA remain visible early.
3. After a run, render tabs: `Summary`, `Academic Trace`, `Path Player`, and `Report`.
4. Show Algorithm Certificate in Summary and expanded trace/glossary in Academic Trace.
5. Add small benchmark table using deterministic presets with `max_trace_rows=0`.
6. Add `st.download_button` for Markdown report export.

## Success Criteria

- [x] A* with `linear_conflict` runs from the UI.
- [x] Summary tab shows metrics and certificate.
- [x] Academic Trace tab shows new trace columns and glossary.
- [x] Path Player remains functional.
- [x] Report tab downloads Markdown.
- [x] Presets and benchmark do not make the first viewport unusable.
