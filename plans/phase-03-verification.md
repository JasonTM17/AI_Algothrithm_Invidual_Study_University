---
phase: 3
title: Verification
status: completed
priority: P1
effort: 45m
dependencies:
  - 1
  - 2
---

# Phase 3: Verification

## Overview

Verify trace hardening with core tests, package tests, compile checks, and a
small manual trace sample.

## Requirements

- Functional: all existing and new behavior tests pass.
- Non-functional: no compile errors or stale generated artifacts.

## Implementation Steps

1. Run `python .\tests\test_search_behavior.py`.
2. Run `python .\eight_puzzle_search_app.py --self-test`.
3. Run `python .\8_puzzle_ai\tests\test_puzzle.py`.
4. Run `python -m py_compile` on canonical app and package app.
5. Re-run a compact trace sample for BFS, A*, IDA*, Local Beam, and SA.

## Success Criteria

- [ ] Verification commands exit 0.
- [ ] Manual sample confirms corrected Node/Frontier/Reached semantics.
