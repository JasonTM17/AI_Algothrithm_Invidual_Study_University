---
phase: 4
title: Submission Pack Exports
status: completed
priority: P2
effort: 2h
dependencies:
  - 1
  - 2
---

# Phase 4: Submission Pack Exports

## Overview

Complete the requested final coursework export helpers: markdown, HTML, DOCX, PDF, CSV, trace replay, search-tree preview, guarantee matrix, depth presets, and heuristic dominance demo.

## Requirements
- Functional: add stdlib-only DOCX/PDF/HTML/CSV export pack.
- Functional: add trace replay and search-tree preview helpers.
- Functional: add deterministic depth presets and heuristic dominance demo.
- Non-functional: no mandatory third-party document dependencies.

## Architecture
All public helper APIs live in `eight_puzzle_search_app.py`; Streamlit calls them for downloads and visual previews.

## Related Code Files
- Modify: `eight_puzzle_search_app.py`
- Modify: `streamlit_eight_puzzle_app.py`
- Modify: `tests/test_search_behavior.py`

## Implementation Steps

1. Add `algorithm_guarantee_matrix`, `build_trace_replay`, and `build_search_tree_preview`.
2. Add depth presets and heuristic dominance demo.
3. Add markdown/HTML/DOCX/PDF/CSV submission pack exports.
4. Add Streamlit download buttons for every export format.
5. Test binary signatures and key report content.

## Success Criteria

- [ ] DOCX starts with ZIP signature and contains required OOXML parts.
- [ ] PDF starts with `%PDF` and includes report title text.
- [ ] HTML/Markdown/CSV include certificate, trace, benchmark, and heuristic dominance sections.
