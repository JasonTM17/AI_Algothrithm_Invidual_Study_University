---
title: AI Coursework Lab Final Polish + GitHub Publication
description: >-
  Finalize the canonical 8-puzzle coursework lab for submission and GitHub
  publication: clean tracked files, polished academic documentation, UI grading
  checklist, automated verification, and remote publication.
status: completed
priority: P2
branch: ''
tags: []
blockedBy: []
blocks: []
created: '2026-06-07T15:06:17.267Z'
createdBy: 'ck:plan'
source: skill
---

# AI Coursework Lab Final Polish + GitHub Publication

## Overview

This plan prepares the project for a personal AI coursework submission and a
clean GitHub publication. The canonical app remains
`eight_puzzle_search_app.py` + `streamlit_eight_puzzle_app.py`; the
`8_puzzle_ai/` package stays educational/supporting.

Acceptance criteria:
- The repository has Git metadata, a clean ignore policy, and the requested
  GitHub remote configured.
- README and `docs/demo_script.md` explain how to run, demo, test, and grade
  the project.
- The Streamlit UI exposes a compact grading checklist and keeps h(n) limited
  to `misplaced` and `manhattan`.
- CI can run the same self-test, behavior tests, package tests, and py_compile
  commands used locally.
- Publication verification confirms there are no logs/cache files staged for
  the initial GitHub commit.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [GitHub Readiness](./phase-01-github-readiness.md) | Completed |
| 2 | [Documentation Polish](./phase-02-documentation-polish.md) | Completed |
| 3 | [Academic UI Polish](./phase-03-academic-ui-polish.md) | Completed |
| 4 | [Testing And CI](./phase-04-testing-and-ci.md) | Completed |
| 5 | [Publication Verification](./phase-05-publication-verification.md) | Completed |

## Dependencies

<!-- Cross-plan dependencies -->
