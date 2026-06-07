---
phase: 1
title: Audit & Canonicalize
status: completed
priority: P2
effort: 30m
dependencies: []
---

# Phase 1: Audit & Canonicalize

## Overview

Confirm the canonical app path and update documentation so users run the correct implementation.

## Requirements
- Functional: README points to `eight_puzzle_search_app.py` and `streamlit_eight_puzzle_app.py` as the main app.
- Non-functional: Keep the auxiliary `8_puzzle_ai/` package documented as secondary/educational.

## Architecture
The root-level module remains the canonical engine and the root Streamlit file remains the canonical UI. The package app is retained but no longer presented as the primary run path.

## Related Code Files
- Modify: `README.md`
- Modify: `8_puzzle_ai/README.md`

## Implementation Steps

1. Update run instructions and project structure notes.
2. Document that CSP/adversarial/complex-environment algorithms are educational demos.
3. Avoid introducing new frameworks or project layout churn.

## Success Criteria

- [x] README clearly identifies the canonical core and UI.
- [x] Package README no longer implies it is the primary app.
