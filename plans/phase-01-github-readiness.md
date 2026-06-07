---
phase: 1
title: GitHub Readiness
status: completed
priority: P1
effort: 1h
dependencies: []
---

# Phase 1: GitHub Readiness

## Overview

Prepare the workspace to become a clean GitHub repository without committing
runtime logs, Python caches, Streamlit state, or temporary browser artifacts.

## Implementation Steps

1. Add `.gitignore` for Python, Streamlit, Playwright, logs, generated reports,
   and temporary screenshots.
2. Initialize Git only after ignore rules exist.
3. Rename the branch to `main`.
4. Add remote `origin` pointing to the requested GitHub repository.
5. Before committing, inspect `git status --ignored` and stage only intentional
   source, tests, docs, plan, and CI files.

## Success Criteria

- [ ] `.gitignore` excludes cache/log/generated artifacts.
- [ ] `.git` exists and branch is `main`.
- [ ] `origin` remote is configured.
- [ ] No runtime log/cache artifact is staged.
