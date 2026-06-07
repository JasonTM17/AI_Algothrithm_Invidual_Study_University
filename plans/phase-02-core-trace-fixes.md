---
phase: 2
title: Core Trace Fixes
status: completed
priority: P1
effort: 2h
dependencies:
  - 1
---

# Phase 2: Core Trace Fixes

## Overview

Apply focused core fixes so trace rows explain search steps consistently.

## Requirements

- Functional: BFS/DFS/UCS/Greedy/A* frontier snapshots show the post-expansion
  frontier for expanded nodes.
- Functional: IDA* pruned nodes must report zero generated children.
- Functional: Local Beam generated-child counts must reflect unique successors,
  not current beam size.
- Functional: Simulated Annealing trace `Node` must be the state evaluated
  before the accept/reject decision.
- Compatibility: keep `TRACE_COLUMNS` unchanged.

## Implementation Steps

1. Move graph-search trace writes after child insertion when the node is
   actually expanded.
2. Split IDA* threshold pruning from child generation.
3. Reorder Local Beam trace generation around candidate creation.
4. Store SA `current_before` for trace rows and keep decision notes explicit.
5. Add regression tests for each corrected semantic.

## Success Criteria

- [ ] Existing solution costs and validation behavior remain unchanged.
- [ ] New tests fail on the old trace semantics and pass after the fix.
