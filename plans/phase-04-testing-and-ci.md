---
phase: 4
title: Testing And CI
status: completed
priority: P1
effort: 1h
dependencies:
  - 3
---

# Phase 4: Testing And CI

## Overview

Add repeatable local and GitHub verification for the canonical app, package
adapter, and Python syntax.

## Implementation Steps

1. Add `requirements.txt` for the canonical Streamlit app.
2. Add GitHub Actions workflow that installs dependencies and runs the local
   verification commands.
3. Run self-test, behavior tests, package tests, and py_compile locally.
4. Start Streamlit and verify desktop/mobile smoke scenarios when possible.

## Success Criteria

- [ ] `python .\eight_puzzle_search_app.py --self-test` passes.
- [ ] `python .\tests\test_search_behavior.py` passes.
- [ ] `python .\8_puzzle_ai\tests\test_puzzle.py` passes.
- [ ] `python -m py_compile ...` passes.
- [ ] GitHub Actions workflow uses the same command set.
