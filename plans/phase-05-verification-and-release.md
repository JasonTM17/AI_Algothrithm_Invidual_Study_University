---
phase: 5
title: "Verification And Release"
status: pending
priority: P1
effort: "2h"
dependencies: [4]
---

# Phase 5: Verification And Release

## Overview

Verify the polished app as a submission-ready Streamlit coursework project,
then commit and push only intentional source/docs/test changes.

## Implementation Steps

1. Run local command suite:
   - `python .\eight_puzzle_search_app.py --self-test`
   - `python .\tests\test_search_behavior.py`
   - `python .\8_puzzle_ai\tests\test_puzzle.py`
   - `python -m py_compile .\eight_puzzle_search_app.py .\streamlit_eight_puzzle_app.py .\8_puzzle_ai\app.py`
2. Run Streamlit on port 8514 or next free port.
3. Playwright desktop 1280x720:
   - first viewport readable;
   - A* + Manhattan runs;
   - Summary/Trace/Heuristics/Experiment/Report tabs render;
   - Report Pack downloads appear.
4. Playwright mobile 390x844:
   - no horizontal scroll;
   - board/CTA usable;
   - trace/search-tree cards do not overflow.
5. Check browser console for app errors; tolerate only known Streamlit internal
   dropdown warnings if no app error is present.
6. Run `git status --short --ignored`; ensure logs/cache/screenshots are ignored.
7. Commit with a focused message and push to `origin/main`.

## Success Criteria

- [ ] All core/package/compile tests pass.
- [ ] Desktop and mobile UI smoke checks pass.
- [ ] No `linear_conflict` option appears in the canonical UI.
- [ ] Report export still includes certificate, PEAS, trace preview, checklist,
      benchmark, and conclusion.
- [ ] GitHub Actions workflow remains aligned with local verification commands.
- [ ] Final branch is clean except ignored artifacts.
