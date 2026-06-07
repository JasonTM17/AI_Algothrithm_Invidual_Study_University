---
phase: 3
title: UI Redesign
status: completed
priority: P2
effort: 2h
dependencies:
  - 1
  - 2
---

# Phase 3: UI Redesign

## Overview

Polish the canonical Streamlit UI while keeping it lightweight and classroom-friendly.

## Requirements
- Functional: Users can see boards, select algorithm/heuristic, run, compare, inspect academic context, and replay path.
- Non-functional: Mobile-first layout, no horizontal scroll, concise first viewport, clearer board and metric presentation.

## Architecture
Keep Streamlit only. Move advanced controls into an expander, move academic context below the run area, and add CSS tokens for board, panels, and metrics.

## Related Code Files
- Modify: `streamlit_eight_puzzle_app.py`

## Implementation Steps

1. Add page-level CSS for theme, compact header, board cells, and metric cards.
2. Shorten the title and place primary controls near the boards.
3. Collapse advanced controls in the sidebar.
4. Render run summary as metric cards before detailed tables.
5. Keep all labels textual and accessible.

## Success Criteria

- [x] Desktop shows board and run controls without layout overlap.
- [x] Mobile shows title, board, and run CTA early.
- [x] Academic content no longer blocks primary workflow.
