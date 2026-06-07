---
phase: 2
title: Documentation Polish
status: completed
priority: P1
effort: 2h
dependencies:
  - 1
---

# Phase 2: Documentation Polish

## Overview

Make the coursework intent obvious to a lecturer opening the repository:
quick-start commands, algorithm groups, PEAS, problem formulation, heuristic
scope, demo script, and grading checklist.

## Implementation Steps

1. Add README quick-start, canonical entrypoint, and test command summary.
2. Add `docs/demo_script.md` with a teacher-facing demo flow.
3. Document that h(n) in the main UI intentionally uses only `misplaced` and
   `manhattan`.
4. Document that Complex Environment, CSP, and Adversarial/Stochastic entries
   are educational models, not standard deterministic 8-puzzle solvers.
5. Include a submission checklist covering algorithms, PEAS, trace,
   Frontier/Reached semantics, report exports, and tests.

## Success Criteria

- [ ] README has a clear first-screen quick start.
- [ ] Demo script includes A*, BFS/UCS/A* comparison, unsolvable, partial goal,
      CSP, and adversarial demos.
- [ ] Documentation matches the actual UI heuristic dropdown.
