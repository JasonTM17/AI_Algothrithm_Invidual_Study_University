---
phase: 2
title: "First Viewport Demo Flow"
status: pending
priority: P1
effort: "3h"
dependencies: [1]
---

# Phase 2: First Viewport Demo Flow

## Overview

Make the first screen faster to understand and operate during a live coursework
demo: the lecturer should immediately see the puzzle, the goal, the chosen
algorithm, and the main Run button.

## Implementation Steps

1. Restructure the top layout into a compact workbench:
   - Left: Start board, Goal board, preset/load/shuffle, manual input expander.
   - Right: algorithm group, algorithm, heuristic, h(n) usage note, Run/Compare.
2. Keep sidebar for secondary controls only: language, max expansions, and
   advanced settings; avoid duplicating controls that already appear in the
   first viewport.
3. Add a compact "Demo Readiness" strip near Run showing preset, solvable status,
   selected group, and whether this algorithm is a standard solver or educational
   model.
4. For `Partially Observable Search`, surface partial-goal controls next to the
   algorithm selection and show the parsed pattern immediately.
5. Keep Goal always visible; never hide it behind an expander.
6. Make button text specific: `Chạy thuật toán đã chọn`, `So sánh thuật toán`,
   `Random Goal một phần`.

## Success Criteria

- [ ] Desktop 1280x720: Start, Goal, selected algorithm, heuristic, and Run CTA
      are visible without scrolling.
- [ ] Mobile 390x844: no horizontal scroll; Start/Goal and Run CTA appear early
      in the page.
- [ ] The UI never suggests `linear_conflict` in the canonical heuristic dropdown.
- [ ] Partially observable demo supports both lecturer-entered and random partial
      goal patterns.
- [ ] No duplicate primary controls create confusing state mismatches.
