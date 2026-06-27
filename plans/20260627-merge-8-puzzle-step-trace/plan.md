# Merge 8-Puzzle Step Trace

Status: completed; locally merged to `main`

## Phases

1. Preserve the dirty `main` worktree on `codex/merge-8-puzzle-step-trace`.
2. Keep the selected Start/config stable and strengthen result certificates.
3. Add independent manual/autoplay players for solution paths and search traces.
4. Add algorithm/UI regression tests and update user-facing documentation.
5. Run all quality gates, then merge the verified branch into local `main`.

## Dependencies

- Streamlit 1.52.2 fragment reruns for non-blocking autoplay.
- Existing `SearchResult`, trace rows, and `Node / Frontier / Reached` contract.

## Acceptance Criteria

- Run and Compare never replace the displayed Start state.
- Compared algorithms share Start, heuristic, seed, limits, and successor order.
- Playback supports Previous, Next, Play, Pause, Reset, speed, and direct step selection.
- Certificates distinguish verified path, reached goal, termination reason, and proven optimality.
- Existing and new core/UI tests pass before local merge to `main`.

## Verification

- `python -m py_compile ...`
- `python .\eight_puzzle_search_app.py --self-test`
- `python .\tests\test_search_behavior.py`
- `python .\tests\test_streamlit_constraint_graph_routing.py`
- `python .\8_puzzle_ai\tests\test_puzzle.py`
- `python -m pytest -q`
- `git diff --check`
