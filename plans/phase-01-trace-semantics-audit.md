---
phase: 1
title: Trace Semantics Audit
status: completed
priority: P1
effort: 45m
dependencies: []
---

# Phase 1: Trace Semantics Audit

## Overview

Review every trace-producing algorithm and classify whether `Node`, `Frontier`,
`Reached`, `Generated Children`, and `Skipped States` match the academic story
shown in the UI/report.

## Requirements

- Functional: identify concrete trace semantics gaps only; do not change
  algorithm result semantics.
- Non-functional: keep old trace columns stable and additive where possible.

## Implementation Steps

1. Inspect BFS, DFS, UCS, Greedy, A*, IDS, IDA*, hill climbing, Local Beam, and
   Simulated Annealing trace code.
2. Run a small trace sample to confirm observed behavior.
3. Decide exact fixes for incorrect or ambiguous rows.

## Success Criteria

- [ ] All trace gaps are listed with algorithm and observed symptom.
- [ ] Fix scope is limited to trace metadata and tests.
