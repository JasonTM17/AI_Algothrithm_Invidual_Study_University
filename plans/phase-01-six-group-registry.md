---
phase: 1
title: Six-Group Registry
status: completed
priority: P1
effort: 1h
dependencies: []
---

# Phase 1: Six-Group Registry

## Overview

Expose the full coursework algorithm catalog in the canonical core registry, preserving existing names and adding the missing complex-environment, CSP, and adversarial/stochastic groups.

## Requirements
- Functional: add all 27 required algorithm entries with group, completeness, optimality, and suitability metadata.
- Functional: add priority/selection rules and aliases for common names such as IDDFS, Alpha Beta, and Min Conflicts.
- Non-functional: keep existing public names backward-compatible and do not change standard algorithm semantics.

## Architecture
`eight_puzzle_search_app.py` remains the canonical registry. UI and tests consume this registry instead of duplicating algorithm lists.

## Related Code Files
- Modify: `eight_puzzle_search_app.py`
- Modify: `tests/test_search_behavior.py`

## Implementation Steps

1. Audit current `ALGORITHM_INFO`, `PRIORITY_RULES`, aliases, and `DEFAULT_ALGORITHMS`.
2. Add missing group names and algorithms from the user coursework spec.
3. Add helper functions for grouping and theory matrix so UI can render group-first selection.
4. Add tests that assert registry coverage for all six groups and all 27 algorithms.

## Success Criteria

- [ ] All 27 algorithm names are present in `DEFAULT_ALGORITHMS`.
- [ ] Six group names are represented exactly once in the registry.
- [ ] Existing algorithms keep their current canonical names.
