---
phase: 4
title: Submission Readiness
status: completed
priority: P2
effort: 2h
dependencies:
  - 1
  - 2
  - 3
---

# Phase 4: Submission Readiness

## Overview

Complete tests, documentation, py_compile, and browser smoke verification for
coursework submission readiness.

## Requirements

- Functional: report export includes run details, heuristic inspector,
  experiment summary, certificate, path, trace preview, and conclusion.
- Non-functional: no new compile errors or known UI console errors.
- Documentation: README mentions the new showcase workflow.

## Architecture

Verification stays local: Python scripts for core behavior, Streamlit for UI,
and Playwright browser checks for desktop/mobile layout smoke tests.

## Related Code Files

- Modify: `README.md`
- Modify: `tests/test_search_behavior.py`

## Implementation Steps

1. Add tests for new public helpers and report content.
2. Update README with the new demo workflow and export features.
3. Run self-test, behavior tests, package tests, and py_compile.
4. Start Streamlit on port 8502 and inspect desktop/mobile with Playwright.
5. Mark ClaudeKit phases completed only after verification passes.

## Success Criteria

- [ ] Core tests and package tests pass.
- [ ] `py_compile` passes for canonical app and package app.
- [ ] Browser smoke checks pass on desktop and mobile.
