"""Streamlit routing and playback regression tests."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import eight_puzzle_search_app as puzzle
from web.algorithm_demo_assets import algorithm_demo_path, algorithm_demo_slug
from web.ui_views import persist_game_image


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


def test_image_game_page_uses_native_streamlit_game() -> None:
    combined = "\n".join(
        [
            _source("streamlit_eight_puzzle_app.py"),
            _source("web/ui_views.py"),
        ]
    )
    css = _source("web/ui-theme.css")

    assert "sidebar_game" not in combined
    assert "st.components.v1.html" not in combined
    assert "get_sidebar_game_html" not in combined
    assert "image-game-hero" in css
    assert "stFileUploaderDropzone" in css
    assert "image-game-board-card" in css


def _open_image_game_page() -> AppTest:
    app = AppTest.from_file(str(ROOT / "streamlit_eight_puzzle_app.py"), default_timeout=30).run()
    assert not app.exception
    app.radio(key="feature_mode").set_value("Trò chơi xếp hình từ ảnh").run()
    assert not app.exception
    return app


def test_streamlit_image_game_native_controls() -> None:
    app = _open_image_game_page()
    initial_start = tuple(app.session_state["start_state"])
    initial_game = tuple(app.session_state["game_state"])
    legal_tiles = {
        initial_game[next_state.index(0)]
        for _action, next_state in puzzle.neighbors(initial_game)
    }
    movable_tile = next(tile for tile in initial_game if tile in legal_tiles)
    movable_index = initial_game.index(movable_tile)

    app.button(key=f"play_tile_{movable_index}_{movable_tile}_0").click().run()
    assert not app.exception
    moved_game = tuple(app.session_state["game_state"])
    assert moved_game != initial_game
    assert app.session_state["game_moves"] == 1
    assert len(app.session_state["game_history"]) == 1
    assert tuple(app.session_state["start_state"]) == initial_start

    app.button(key="game_undo").click().run()
    assert tuple(app.session_state["game_state"]) == initial_game
    assert app.session_state["game_moves"] == 0
    assert not app.session_state["game_history"]

    app.button(key="game_shuffle").click().run()
    shuffled_game = tuple(app.session_state["game_state"])
    assert shuffled_game != initial_game
    assert tuple(app.session_state["start_state"]) == initial_start
    assert app.session_state["game_moves"] == 0

    app.button(key="game_reset").click().run()
    assert tuple(app.session_state["game_state"]) == shuffled_game
    assert tuple(app.session_state["start_state"]) == initial_start

    app.button(key="game_use_start").click().run()
    assert tuple(app.session_state["start_state"]) == shuffled_game
    assert tuple(app.session_state["game_initial_state"]) == shuffled_game


def test_persist_game_image_accepts_uploaded_file_like_object() -> None:
    class FakeUpload:
        name = "tiny.png"
        type = "image/png"

        def getvalue(self) -> bytes:
            return b"fake-png-bytes"

    st.session_state.game_image_signature = ""
    st.session_state.game_image_url = ""
    st.session_state.game_image_name = ""

    assert persist_game_image(FakeUpload())
    assert st.session_state.game_image_name == "tiny.png"
    assert st.session_state.game_image_signature == "tiny.png:14"
    assert st.session_state.game_image_url.startswith("data:image/png;base64,")
    assert not persist_game_image(FakeUpload())


def test_algorithm_demo_gifs_cover_all_registered_algorithms() -> None:
    generator = _source("scripts/generate-algorithm-demo-gifs.py")
    app_source = _source("streamlit_eight_puzzle_app.py")

    assert "puzzle.run_algorithm(DEMO_START, algorithm" in generator
    assert "show_algorithm_demo(algorithm, lang)" in app_source
    assert algorithm_demo_slug("A*") == "a-star"
    assert algorithm_demo_slug("Alpha-Beta Pruning") == "alpha-beta-pruning"

    for algorithm in puzzle.DEFAULT_ALGORITHMS:
        path = algorithm_demo_path(algorithm)
        assert path.is_file(), f"Missing GIF for {algorithm}: {path}"
        assert path.stat().st_size > 20_000, f"GIF is unexpectedly small for {algorithm}"
        with Image.open(path) as gif:
            assert gif.format == "GIF"
            assert gif.n_frames >= 3, f"GIF should be animated for {algorithm}"
            assert gif.size == (800, 450)


def test_readme_embeds_each_algorithm_demo_gif() -> None:
    readme = _source("README.md")

    assert "GIF demo trực tiếp cho từng thuật toán" in readme
    for algorithm in puzzle.DEFAULT_ALGORITHMS:
        relative_path = algorithm_demo_path(algorithm).relative_to(ROOT).as_posix()
        assert f'<img src="{relative_path}"' in readme, f"README missing GIF for {algorithm}"
        assert f'alt="{algorithm} demo"' in readme, f"README missing alt text for {algorithm}"


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
        test_image_game_page_uses_native_streamlit_game,
        test_streamlit_image_game_native_controls,
        test_persist_game_image_accepts_uploaded_file_like_object,
        test_algorithm_demo_gifs_cover_all_registered_algorithms,
        test_readme_embeds_each_algorithm_demo_gif,
        test_streamlit_run_compare_and_playback_controls,
    ]
    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")


if __name__ == "__main__":
    run_all_tests()
