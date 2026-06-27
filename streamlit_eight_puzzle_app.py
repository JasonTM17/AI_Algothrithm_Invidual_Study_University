"""Bilingual Streamlit UI orchestrator for the 8-puzzle search visualizer."""

from __future__ import annotations

from html import escape
from typing import Any, Optional

import streamlit as st

import eight_puzzle_search_app as puzzle
from web.ui_theme import apply_theme
from web.ui_text import HELP, text, help_text, localize_table, localize_trace_text, localize_algorithm_group
from web.ui_views import (
    show_page_header, show_image_puzzle_page,
    show_goal_panel, show_board, heuristic_usage_note, show_grading_checklist,
    show_peas_model, show_problem_variant, show_academic_context, show_result,
    show_experiment_lab, show_interactive_game_panel,
    show_path_player, show_certificate, show_trace_story, show_trace_replay_player,
    show_heuristic_inspector, show_priority_basis, show_algorithm_profile,
    current_partial_goal_pattern, partial_goal_controls,
    reset_game_state, clear_solver_outputs, load_demo_preset,
    reset_playback_state,
    shuffle_start_state, current_shuffle_note,
    demo_readiness_html, trace_run_guide_html, board_matrix_html, metric_cards_html,
    image_board_html, playable_tile_grid, persist_game_image,
    certificate_chips_html, certificate_rows, trace_glossary_rows,
    academic_problem_markdown, readiness_chip, trace_detail_card,
    caro_demo_panel_html,
)



def build_config(seed_override: Optional[int] = None, randomize_successors: bool = False) -> puzzle.TraceConfig:
    return puzzle.TraceConfig(
        max_expansions=st.session_state.max_expansions,
        max_trace_rows=st.session_state.max_trace_rows,
        frontier_preview=st.session_state.frontier_preview,
        reached_preview=st.session_state.reached_preview,
        ids_max_depth=st.session_state.ids_depth,
        ida_max_iterations=st.session_state.ida_iterations,
        local_max_steps=st.session_state.local_steps,
        random_restarts=st.session_state.random_restarts,
        beam_width=st.session_state.beam_width,
        seed=st.session_state.seed if seed_override is None else seed_override,
        randomize_successors=randomize_successors,
        sa_initial_temp=st.session_state.sa_initial_temp,
        sa_cooling_rate=st.session_state.sa_cooling_rate,
        sa_min_temp=st.session_state.sa_min_temp,
        sa_max_steps=st.session_state.sa_max_steps,
        partial_goal_pattern=current_partial_goal_pattern(),
    )


def initialize_state() -> None:
    if "start_state" not in st.session_state:
        st.session_state.start_state = puzzle.generate_random_state(20, seed=1)
    if "shuffle_count" not in st.session_state:
        st.session_state.shuffle_count = 0
    if "last_shuffle_moves" not in st.session_state:
        st.session_state.last_shuffle_moves = 20
    if "last_shuffle_seed" not in st.session_state:
        st.session_state.last_shuffle_seed = 1
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_result_heuristic" not in st.session_state:
        st.session_state.last_result_heuristic = "manhattan"
    if "last_comparison" not in st.session_state:
        st.session_state.last_comparison = None
    if "last_benchmark" not in st.session_state:
        st.session_state.last_benchmark = None
    if "last_experiment" not in st.session_state:
        st.session_state.last_experiment = None
    if "last_experiment_heuristic" not in st.session_state:
        st.session_state.last_experiment_heuristic = "manhattan"
    if "last_preset_name" not in st.session_state:
        st.session_state.last_preset_name = ""
    if "last_submission_pack" not in st.session_state:
        st.session_state.last_submission_pack = None
    if "last_submission_pack_key" not in st.session_state:
        st.session_state.last_submission_pack_key = ""
    if "partial_goal_pattern_text" not in st.session_state:
        st.session_state.partial_goal_pattern_text = "1 2 ? ? ? ? ? ? ?"
    if "game_state" not in st.session_state:
        st.session_state.game_state = st.session_state.start_state
    if "game_moves" not in st.session_state:
        st.session_state.game_moves = 0
    if "game_history" not in st.session_state:
        st.session_state.game_history = []
    if "game_message" not in st.session_state:
        st.session_state.game_message = ""
    if "game_image_url" not in st.session_state:
        st.session_state.game_image_url = ""
    if "game_image_name" not in st.session_state:
        st.session_state.game_image_name = ""
    if "game_image_signature" not in st.session_state:
        st.session_state.game_image_signature = ""


def main() -> None:
    st.set_page_config(
        page_title="8-Puzzle Search",
        page_icon="🧩",
        layout="wide",
        menu_items={"Get Help": None, "Report a bug": None, "About": None},
    )
    apply_theme()
    initialize_state()

    with st.sidebar:
        language_choice = st.selectbox(
            "Ngôn ngữ / Language",
            ["Tiếng Việt", "English"],
            index=0,
            key="language_choice",
            help=HELP["vi"]["language"],
        )
        lang = "vi" if language_choice == "Tiếng Việt" else "en"
        feature_options = [
            text(lang, "feature_puzzle"),
            text(lang, "feature_image_puzzle"),
        ]
        feature_mode = st.radio(text(lang, "feature_mode"), feature_options, key="feature_mode")

        if feature_mode == text(lang, "feature_puzzle"):
            st.header(text(lang, "controls"))
            st.number_input(text(lang, "max_expansions"), min_value=1, max_value=200000, value=5000, key="max_expansions", help=help_text(lang, "max_expansions"))
            with st.expander(text(lang, "advanced_settings"), expanded=False):
                st.number_input(text(lang, "seed"), min_value=0, max_value=1_000_000, value=1, key="seed", help=help_text(lang, "seed"))
                st.number_input(text(lang, "max_trace_rows"), min_value=0, max_value=5000, value=300, key="max_trace_rows", help=help_text(lang, "max_trace_rows"))
                st.number_input(text(lang, "frontier_preview"), min_value=1, max_value=30, value=5, key="frontier_preview", help=help_text(lang, "frontier_preview"))
                st.number_input(text(lang, "reached_preview"), min_value=1, max_value=30, value=5, key="reached_preview", help=help_text(lang, "reached_preview"))
                st.number_input(text(lang, "ids_depth"), min_value=1, max_value=80, value=30, key="ids_depth", help=help_text(lang, "ids_depth"))
                st.number_input(text(lang, "ida_iterations"), min_value=1, max_value=200, value=80, key="ida_iterations", help=help_text(lang, "ida_iterations"))
                st.number_input(text(lang, "local_steps"), min_value=1, max_value=5000, value=200, key="local_steps", help=help_text(lang, "local_steps"))
                st.number_input(text(lang, "random_restarts"), min_value=0, max_value=200, value=20, key="random_restarts", help=help_text(lang, "random_restarts"))
                st.number_input(text(lang, "beam_width"), min_value=1, max_value=50, value=4, key="beam_width", help=help_text(lang, "beam_width"))
                st.divider()
                st.number_input(text(lang, "sa_initial_temp"), min_value=1.0, max_value=1000.0, value=100.0, key="sa_initial_temp", help=help_text(lang, "sa_initial_temp"))
                st.number_input(text(lang, "sa_cooling_rate"), min_value=0.9, max_value=0.9999, value=0.995, step=0.001, key="sa_cooling_rate", help=help_text(lang, "sa_cooling_rate"))
                st.number_input(text(lang, "sa_min_temp"), min_value=0.001, max_value=1.0, value=0.01, key="sa_min_temp", help=help_text(lang, "sa_min_temp"))
                st.number_input(text(lang, "sa_max_steps"), min_value=100, max_value=50000, value=5000, key="sa_max_steps", help=help_text(lang, "sa_max_steps"))

    if feature_mode == text(lang, "feature_image_puzzle"):
        show_image_puzzle_page(lang)
        return
        
    show_page_header(lang)

    grouped_algorithms = puzzle.algorithms_by_group()
    groups = puzzle.algorithm_groups()
    default_group = puzzle.ALGORITHM_INFO["A*"]["group"]

    col_left, col_right = st.columns([1, 1.45], gap="large")
    with col_left:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="panel-heading">
                  <h2>{escape(text(lang, "board_panel"))}</h2>
                  <span class="panel-badge">{escape(text(lang, "state_lab"))}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            preset_name = st.selectbox(text(lang, "demo_preset"), list(puzzle.DEMO_PRESETS.keys()), key="main_preset_name")
            if st.button(text(lang, "load_preset"), width="stretch", key="main_load_preset"):
                load_demo_preset(preset_name)
                st.rerun()
            scramble = st.slider(text(lang, "scramble_moves"), min_value=0, max_value=80, value=20, key="scramble_moves", help=help_text(lang, "scramble_moves"))
            if st.button(text(lang, "shuffle"), type="primary", width="stretch", key="main_shuffle", help=help_text(lang, "shuffle")):
                shuffle_start_state(scramble)
            st.caption(current_shuffle_note(lang))

            show_board(text(lang, "start_state"), st.session_state.start_state, lang, "start_board")
            show_goal_panel(lang)
            manual_label = text(lang, "manual_start_input")
            with st.expander(manual_label, expanded=False):
                state_text = st.text_input(
                    text(lang, "custom_start"),
                    value=" ".join(str(x) for x in st.session_state.start_state),
                    help=help_text(lang, "custom_start"),
                )
                if st.button(text(lang, "use_custom"), help=help_text(lang, "use_custom")):
                    try:
                        st.session_state.start_state = puzzle.parse_state(state_text)
                        reset_game_state(st.session_state.start_state)
                        clear_solver_outputs()
                        st.session_state.last_preset_name = ""
                        st.rerun()
                    except ValueError as exc:
                        invalid_prefix = "Invalid state" if lang == "en" else "Ma trận không hợp lệ"
                        invalid_hint = (
                            "Enter 9 numbers 0-8 separated by spaces. Example: 1 2 3 4 5 6 0 7 8"
                            if lang == "en"
                            else "Nhập 9 số từ 0 đến 8, cách nhau bởi dấu cách. Ví dụ: 1 2 3 4 5 6 0 7 8"
                        )
                        st.error(f"{invalid_prefix}: {exc}. {invalid_hint}")

    with col_right:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="panel-heading">
                  <h2>{escape(text(lang, "run"))}</h2>
                  <span class="panel-badge">{escape(text(lang, "algorithm_cockpit"))}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            algorithm_group = st.selectbox(
                text(lang, "algorithm_group"),
                groups,
                index=groups.index(default_group) if default_group in groups else 0,
                format_func=lambda group: localize_algorithm_group(group, lang),
                help=help_text(lang, "algorithm"),
            )
            group_algorithms = grouped_algorithms[algorithm_group]
            algorithm = st.selectbox(
                text(lang, "algorithm"),
                group_algorithms,
                index=group_algorithms.index("A*") if "A*" in group_algorithms else 0,
                help=help_text(lang, "algorithm"),
            )
            heuristic = st.selectbox(
                text(lang, "heuristic"),
                puzzle.DEFAULT_HEURISTICS,
                index=puzzle.DEFAULT_HEURISTICS.index("manhattan"),
                help=help_text(lang, "heuristic"),
            )
            st.markdown(demo_readiness_html(lang, algorithm, heuristic), unsafe_allow_html=True)
            st.markdown(caro_demo_panel_html(lang, algorithm), unsafe_allow_html=True)
            st.caption(f"{text(lang, 'heuristic_usage')}: {localize_trace_text(heuristic_usage_note(lang, algorithm), lang)}")
            partial_goal_controls(lang, algorithm)
            st.caption(f"{text(lang, 'algorithm')}: {algorithm} | {text(lang, 'heuristic')}: {heuristic}")
            run_clicked = st.button(
                text(lang, "run_selected"),
                type="primary",
                width="stretch",
                help=help_text(lang, "run_selected"),
                key="run_selected_full_width",
            )
            compare_clicked = st.button(
                text(lang, "compare_all"),
                width="stretch",
                help=help_text(lang, "compare_all"),
                key="compare_all_full_width",
            )
            st.caption(localize_trace_text(text(lang, "notes"), lang))

        if run_clicked:
            run_message = (
                f"Running {algorithm} with {heuristic}..."
                if lang == "en"
                else f"Đang chạy {algorithm} với {heuristic}..."
            )
            with st.spinner(run_message):
                config = build_config(randomize_successors=False)
                st.session_state.last_result = puzzle.run_algorithm(st.session_state.start_state, algorithm, heuristic, config)
                st.session_state.last_result_heuristic = heuristic
                st.session_state.last_comparison = None
                reset_playback_state("solution_playback", "trace_playback")
                st.rerun()
        elif compare_clicked:
            algo_count = len(group_algorithms)
            compare_label = (
                f"Comparing {algo_count} algorithms..."
                if lang == "en"
                else f"Đang so sánh {algo_count} thuật toán..."
            )
            complete_label = "Comparison complete!" if lang == "en" else "So sánh hoàn tất!"
            with st.status(compare_label, expanded=True) as status:
                config = build_config(randomize_successors=False)
                st.session_state.last_comparison = puzzle.compare_algorithms(
                    st.session_state.start_state,
                    algorithms=group_algorithms,
                    heuristic=heuristic,
                    config=config,
                )
                st.session_state.last_result = None
                reset_playback_state("solution_playback", "trace_playback")
                status.update(label=complete_label, state="complete")
                st.rerun()

        if st.session_state.last_result is not None:
            st.info(text(lang, "trace_result_hint"))
            show_result(st.session_state.last_result, lang, st.session_state.last_result_heuristic)
        elif st.session_state.last_comparison is not None:
            st.subheader(text(lang, "comparison"))
            st.dataframe(localize_table(st.session_state.last_comparison, lang), width="stretch")
        else:
            st.markdown(
                f"""
                <div class="lab-panel">
                  <strong>{escape(text(lang, "choose_action"))}</strong>
                  <p class="section-note">{escape(text(lang, "choose_action_hint"))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(trace_run_guide_html(lang), unsafe_allow_html=True)

        st.divider()
        show_academic_context(lang, algorithm, heuristic)


if __name__ == "__main__":
    main()
