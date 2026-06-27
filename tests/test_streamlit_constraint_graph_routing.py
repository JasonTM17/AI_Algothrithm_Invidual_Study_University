"""Streamlit routing and playback regression tests."""

from __future__ import annotations

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_graph_coloring_entrypoints_are_removed() -> None:
    combined = "\n".join(
        [
            _source("streamlit_eight_puzzle_app.py"),
            _source("web/ui_views.py"),
            _source("web/ui_text.py"),
            _source("eight_puzzle_search_app.py"),
        ]
    )

    blocked_terms = [
        "Constraint Graph",
        "thu_duc",
        "Thu Duc",
        "Thủ Đức",
        "graph coloring",
        "graph-coloring",
        "show_thu_duc_graph_coloring_page",
        "feature_thu_duc",
    ]
    for term in blocked_terms:
        assert term not in combined


def test_sidebar_features_are_puzzle_only() -> None:
    source = _source("streamlit_eight_puzzle_app.py")
    feature_block = source[source.index("feature_options = [") : source.index("feature_mode = st.radio")]

    assert "feature_puzzle" in feature_block
    assert "feature_image_puzzle" in feature_block
    assert "feature_thu_duc" not in feature_block
    assert "coloring" not in feature_block.lower()


def test_run_and_compare_use_displayed_start() -> None:
    source = _source("streamlit_eight_puzzle_app.py")

    assert "prepare_random_algorithm_run" not in source
    assert source.count("build_config(randomize_successors=False)") == 2


def test_streamlit_run_compare_and_playback_controls() -> None:
    app = AppTest.from_file(str(ROOT / "streamlit_eight_puzzle_app.py"), default_timeout=30).run()
    assert not app.exception
    displayed_start = tuple(app.session_state["start_state"])

    app.button(key="run_selected_full_width").click().run()
    assert not app.exception
    assert tuple(app.session_state["start_state"]) == displayed_start
    assert tuple(app.session_state["last_result"].start) == displayed_start

    for prefix in ("solution_playback", "trace_playback"):
        app.button(key=f"{prefix}_next").click().run()
        assert app.session_state[f"{prefix}_step"] == 1
        app.button(key=f"{prefix}_reset").click().run()
        assert app.session_state[f"{prefix}_step"] == 0
        app.button(key=f"{prefix}_play").click().run()
        assert app.session_state[f"{prefix}_step"] >= 1
        assert app.session_state[f"{prefix}_playing"]
        app.button(key=f"{prefix}_pause").click().run()
        assert not app.session_state[f"{prefix}_playing"]
        assert not app.exception

    compare_app = AppTest.from_file(str(ROOT / "streamlit_eight_puzzle_app.py"), default_timeout=30).run()
    compare_start = tuple(compare_app.session_state["start_state"])
    compare_app.button(key="compare_all_full_width").click().run()
    assert not compare_app.exception
    assert tuple(compare_app.session_state["start_state"]) == compare_start
    assert compare_app.session_state["last_comparison"] is not None


def run_all_tests() -> None:
    tests = [
        test_graph_coloring_entrypoints_are_removed,
        test_sidebar_features_are_puzzle_only,
        test_run_and_compare_use_displayed_start,
        test_streamlit_run_compare_and_playback_controls,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")


if __name__ == "__main__":
    run_all_tests()
