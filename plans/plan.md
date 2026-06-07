---
title: 8-Puzzle UI/UX Beauty + Algorithm Correctness Polish
description: >-
  Polish the 8-Puzzle coursework lab into a cleaner, more beautiful demo while
  preserving algorithm semantics: only UI, explanation, guardrails, trace
  presentation, and verification should change unless a correctness bug is
  proven by tests.
status: completed
priority: P2
branch: main
tags: []
blockedBy: []
blocks: []
created: '2026-06-07T15:30:19.376Z'
createdBy: 'ck:plan'
source: skill
---

# 8-Puzzle UI/UX Beauty + Algorithm Correctness Polish

## Overview

This plan improves the final submission experience for a lecturer/demo audience:
the first viewport should feel polished and easy to operate, algorithm choices
should be impossible to misunderstand, and the trace must continue to represent
real `Node / Frontier / Reached` behavior rather than decorative storytelling.

Acceptance criteria:
- The Streamlit UI has a calmer academic-lab visual system, stronger contrast,
  cleaner spacing, and responsive boards without horizontal scroll.
- The first viewport exposes Start, Goal, preset, algorithm group, algorithm,
  heuristic, and Run CTA without burying the main demo flow.
- The UI clearly distinguishes standard 8-puzzle solvers from educational
  Complex/CSP/Adversarial simulations.
- h(n) remains exactly `misplaced` and `manhattan` in the canonical UI.
- Algorithm traces keep compatible columns and truthfully show `Node`,
  post-expansion `Frontier`, `Reached`, `Priority Rule`, and `Selection Key`.
- Existing self-test, behavior tests, package tests, py_compile, and
  Playwright desktop/mobile checks pass before release.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Design Audit And Visual System](./phase-01-design-audit-and-visual-system.md) | Completed |
| 2 | [First Viewport Demo Flow](./phase-02-first-viewport-demo-flow.md) | Completed |
| 3 | [Algorithm Correctness UX Guards](./phase-03-algorithm-correctness-ux-guards.md) | Completed |
| 4 | [Academic Trace Visualization](./phase-04-academic-trace-visualization.md) | Completed |
| 5 | [Verification And Release](./phase-05-verification-and-release.md) | Completed |

## Dependencies

<!-- Cross-plan dependencies -->
