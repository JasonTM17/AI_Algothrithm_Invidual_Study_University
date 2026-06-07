---
phase: 4
title: Academic Trace Visualization
status: completed
priority: P1
effort: 3h
dependencies:
  - 3
---

# Phase 4: Academic Trace Visualization

## Overview

Upgrade the trace presentation from a raw table into a clearer teaching tool
while preserving the true trace contract and old columns.

## Implementation Steps

1. Keep all existing trace columns compatible: `Node`, `Frontier`, `Reached`,
   `Priority Rule`, `Selection Key`, `Generated Children`, `Skipped States`,
   `Decision/Note`.
2. Add a "Why This Node?" drawer/card for the selected trace row:
   - BFS: FIFO / shallowest.
   - DFS: LIFO / deepest.
   - UCS: min `g(n)`.
   - Greedy/local: min or improved `h(n)`.
   - A*: min `f(n)=g(n)+h(n)`.
   - IDA*: current threshold.
   - SA: `Δh`, temperature, acceptance.
   - CSP/Adversarial: constraint/utility/chance explanation.
3. Improve Trace Player UI:
   - slider row index;
   - show selected node board;
   - show generated children count;
   - show compact Frontier/Reached previews;
   - show "skipped states" explanation.
4. Improve Search Tree Preview for small depth:
   - stacked cards on mobile;
   - mark start/current/goal candidate;
   - show `g/h/f` without implying the tree is exhaustive.
5. Add trace glossary visible near the trace, not buried below unrelated report
   text.

## Success Criteria

- [ ] `max_trace_rows=0` still disables trace without crash.
- [ ] A*/UCS/Greedy trace rows display correct `Selection Key`.
- [ ] IDA* rows expose threshold; SA rows expose temperature/acceptance note.
- [ ] Frontier shown in the trace is post-expansion, not stale pre-expansion.
- [ ] Mobile trace cards fit without horizontal scrolling.
