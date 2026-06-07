---
phase: 2
title: Algorithm Certification
status: completed
priority: P2
effort: 1h
dependencies:
  - 1
---

# Phase 2: Algorithm Certification

## Overview

Add public validation and report-export helpers so each algorithm run can be certified and explained.

## Implementation Steps

1. Add `validate_result(result, heuristic_name, goal=GOAL_STATE) -> dict` with the required fixed keys.
2. Validate path transitions, action count, path cost, terminal goal match, solvability early-stop behavior, and non-negative heuristic values.
3. Add `export_run_markdown(result, heuristic_name, validation) -> str` for submission-ready Markdown.
4. Ensure helper behavior is deterministic and independent of Streamlit.

## Success Criteria

- [x] Valid solved paths pass the certificate.
- [x] Mutated/invalid paths fail with a useful `error`.
- [x] Unsolvable runs certify early rejection with expanded node count zero.
- [x] Exported Markdown includes board states, metrics, certificate, path, trace preview, and academic conclusion.
