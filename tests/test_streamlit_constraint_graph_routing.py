"""Source-level routing checks for the Streamlit CSP graph-coloring demo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _source() -> str:
    return (ROOT / "streamlit_eight_puzzle_app.py").read_text(encoding="utf-8")


def test_no_top_level_8_puzzle_coloring_feature() -> None:
    source = _source()

    assert "Tô màu trạng thái 8-puzzle" not in source
    assert "8-puzzle state coloring" not in source
    assert "Heuristic Coloring" not in source
    assert "show_puzzle_coloring_page" not in source
    assert "feature_coloring" not in source


def test_thu_duc_demo_has_sidebar_and_constraint_graph_entrypoints() -> None:
    source = _source()
    call = "show_thu_duc_graph_coloring_page(lang)"
    guard = 'algorithm_group == "Constraint Satisfaction Problems" and algorithm == "Constraint Graph"'
    sidebar_guard = 'feature_mode == text(lang, "feature_thu_duc")'

    assert call in source
    assert guard in source
    assert sidebar_guard in source
    assert source.count(call) >= 2
    assert source.index(guard) < source.rindex(call)


def test_sidebar_features_keep_thu_duc_without_8_puzzle_coloring() -> None:
    source = _source()
    feature_block = source[source.index("feature_options = [") : source.index("feature_mode = st.radio")]

    assert "feature_puzzle" in feature_block
    assert "feature_image_puzzle" in feature_block
    assert "feature_thu_duc" in feature_block
    assert "feature_coloring" not in feature_block
    assert "coloring" not in feature_block.lower()


def run_all_tests() -> None:
    tests = [
        test_no_top_level_8_puzzle_coloring_feature,
        test_thu_duc_demo_has_sidebar_and_constraint_graph_entrypoints,
        test_sidebar_features_keep_thu_duc_without_8_puzzle_coloring,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")


if __name__ == "__main__":
    run_all_tests()
