---
phase: 3
title: Academic UI Polish
status: completed
priority: P1
effort: 2h
dependencies:
  - 2
---

# Phase 3: Academic UI Polish

## Overview

Add final academic polish to the Streamlit UI while preserving the existing
compact first viewport and canonical solver behavior.

## Implementation Steps

1. Add a shared coursework grading checklist helper in the core.
2. Render the checklist in the Summary and Report tabs.
3. Add a sidebar note explaining whether the selected algorithm uses h(n) for
   node selection or only for visualization/certificate support.
4. Keep the heuristic dropdown restricted to `misplaced` and `manhattan`.
5. Improve localized fallback text for algorithms outside the standard
   solver groups so PEAS/problem/theory panels remain Vietnamese-friendly.

## Success Criteria

- [ ] Every algorithm still renders academic context without English-only
      fallback dominating Vietnamese mode.
- [ ] Non-heuristic algorithms clearly state that h(n) is not their priority.
- [ ] Grading checklist appears in the UI and exported report.
