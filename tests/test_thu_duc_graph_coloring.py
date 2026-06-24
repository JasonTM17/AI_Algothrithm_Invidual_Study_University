"""Regression tests for Thu Duc graph-coloring CSP demo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import thu_duc_graph_coloring as coloring


def test_thu_duc_graph_has_expected_shape() -> None:
    assert len(coloring.REGIONS) == 24
    assert len(coloring.EDGES) == 43
    regions = set(coloring.REGIONS)
    assert all(left in regions and right in regions for left, right in coloring.EDGES)


def test_three_color_solution_is_valid() -> None:
    result = coloring.color_graph(max_colors=3)

    assert result.valid
    assert len(result.colors_used) <= 3
    assert result.conflicts == []


def test_validate_coloring_detects_adjacent_conflict() -> None:
    result = coloring.color_graph(max_colors=4)
    assignments = dict(result.assignments)
    left, right = coloring.EDGES[0]
    assignments[right] = assignments[left]

    assert (left, right) in coloring.validate_coloring(assignments)


def test_coloring_rows_cover_all_regions() -> None:
    result = coloring.color_graph(max_colors=4)
    rows = coloring.coloring_rows(result)

    assert len(rows) == len(coloring.REGIONS)
    assert {row["Region"] for row in rows} == set(coloring.REGIONS)


def run_all_tests() -> None:
    tests = [
        test_thu_duc_graph_has_expected_shape,
        test_three_color_solution_is_valid,
        test_validate_coloring_detects_adjacent_conflict,
        test_coloring_rows_cover_all_regions,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")


if __name__ == "__main__":
    run_all_tests()
