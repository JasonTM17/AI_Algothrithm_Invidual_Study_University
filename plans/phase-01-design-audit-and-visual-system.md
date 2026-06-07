---
phase: 1
title: Design Audit And Visual System
status: completed
priority: P1
effort: 2h
dependencies: []
---

# Phase 1: Design Audit And Visual System

## Overview

Audit the current Streamlit layout and define a restrained academic-lab design
system that improves beauty, readability, and trust without turning the app into
a landing page.

## Implementation Steps

1. Inspect current `apply_theme()`, board CSS, metric cards, tabs, expanders,
   sidebar controls, and mobile behavior.
2. Define UI tokens in existing CSS only: neutral surface, readable ink, teal
   accent, amber warning/accent, consistent 8px radius, stable board dimensions,
   and high contrast for dark/light modes.
3. Replace overly faint text with accessible contrast; keep no decorative blobs,
   no marketing hero, no nested cards.
4. Standardize repeated panels: metric card, certificate chip, grading checklist
   row, PEAS/problem card, trace replay card.
5. Keep the blank tile rendered as visible `0` with underline/dashed accent, not
   an empty black tile.
6. Add a short visual QA checklist to `docs/demo_script.md` or README so the
   final demo can be evaluated consistently.

## Success Criteria

- [ ] Header, subtitle, board labels, sidebar captions, and tab text have strong
      contrast in dark and light mode.
- [ ] Start/Goal boards have stable cell sizes and no layout shift on hover,
      result updates, or mobile resize.
- [ ] UI palette is not dominated by one hue family and remains academic/workful.
- [ ] No new frontend framework or dependency is introduced.
- [ ] Visual changes do not touch algorithm outputs.
