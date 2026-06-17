"""Desktop Tkinter launcher for the 8-Puzzle search visualizer.

Usage:
    python eight_puzzle_tk_app.py              # launch GUI
    python eight_puzzle_tk_app.py --self-test  # headless smoke test
"""

from __future__ import annotations

import argparse
import sys


def self_test() -> int:
    """Verify modules, i18n, widgets, and callback wiring without showing a window."""
    from eight_puzzle_search_app import DEMO_PRESETS, GOAL_STATE
    from eight_puzzle_tk import i18n

    assert i18n.t("app_title", "vi"), "vi title missing"
    assert i18n.t("app_title", "en"), "en title missing"

    try:
        import tkinter as tk
        from eight_puzzle_tk.app import App
    except ImportError as e:
        print(f"tkinter not available: {e}")
        return 1

    root = tk.Tk()
    root.withdraw()
    try:
        app = App(root)

        # Sidebar widgets
        for attr in (
            "preset_combo", "scramble_var", "seed_var",
            "group_combo", "algorithm_combo", "heuristic_combo",
            "limit_vars", "run", "compare_all",
        ):
            assert hasattr(app, attr), f"sidebar widget missing: {attr}"
        assert len(app.limit_vars) >= 5, "limit_vars too small"

        # Main area widgets
        for attr in ("start_editor", "goal_editor", "notebook", "_tab_indices"):
            assert hasattr(app, attr), f"main area widget missing: {attr}"
        assert len(app._tab_indices) == 7, "notebook should have 7 tabs"
        for attr in ("game_moves_var", "game_status_var", "game_hint_var"):
            assert hasattr(app, attr), f"game widget missing: {attr}"
        for attr in ("vacuum_cells", "vacuum_tree", "vacuum_status_var", "vacuum_coloring_note_var"):
            assert hasattr(app, attr), f"vacuum widget missing: {attr}"

        # Preset selection
        first_preset = next(iter(DEMO_PRESETS))
        app.preset_var.set(first_preset)
        app._on_preset_change()
        assert app.start_editor.get_state() == DEMO_PRESETS[first_preset], "preset did not load"

        # Shuffle
        before = app.start_editor.get_state()
        app.scramble_var.set("3")
        app.seed_var.set("7")
        app._on_shuffle()
        after = app.start_editor.get_state()
        assert before != after, "shuffle did not change start state"
        assert app.start_editor.get_state() is not None, "shuffled state is invalid"
        assert app.preset_var.get() == app._t("preset_custom"), "shuffle should reset preset to custom"

        # Group change → algorithm combo updates
        groups = app.algorithm_groups_list
        assert len(groups) >= 3, "should have multiple algorithm groups"
        before_algos = tuple(app.algorithm_combo.cget("values"))
        app.group_var.set(groups[1])
        app._on_group_change()
        after_algos = tuple(app.algorithm_combo.cget("values"))
        assert before_algos != after_algos, "group change should refresh algorithm combo"

        # Language toggle
        app.lang_var.set("en")
        app._on_lang_change()
        assert app.lang == "en", "lang did not switch to en"
        app.lang_var.set("vi")
        app._on_lang_change()
        assert app.lang == "vi", "lang did not switch back to vi"

        # Core search + Summary tab (cụm 3)
        for attr in (
            "summary_status_var", "summary_metrics", "summary_certificate",
            "summary_error_var", "summary_conclusion_var",
        ):
            assert hasattr(app, attr), f"summary widget missing: {attr}"
        assert len(app.summary_metrics) == 11, "expected 11 metric rows"
        assert len(app.summary_certificate) == 5, "expected 5 cert rows"

        app.preset_var.set("easy_2")
        app._on_preset_change()
        app.algorithm_var.set("BFS")
        assert app.start_editor.get_state() == DEMO_PRESETS["easy_2"], "easy_2 preset did not load"
        app._on_game_hint()
        assert "A*" in app.game_hint_var.get() or "Gợi ý" in app.game_hint_var.get(), (
            f"game hint did not render, got {app.game_hint_var.get()!r}"
        )
        before_game_step = app.start_editor.get_state()
        app._on_game_next_step()
        assert app.start_editor.get_state() != before_game_step, "game next step did not move the board"
        assert app.game_move_count == 1, "game move count should increment for AI step"
        app._on_game_reset()
        assert app.start_editor.get_state() == DEMO_PRESETS["easy_2"], "game reset did not restore preset"
        assert app.game_move_count == 0, "game reset should clear move count"
        app._on_run()
        assert app.summary_status_var.get() == app._t("summary_found"), (
            f"expected found status, got {app.summary_status_var.get()!r}"
        )
        assert app.summary_metrics["algorithm"].get() == "BFS"
        assert app.summary_metrics["path_cost"].get() == "2", (
            f"expected path_cost=2 for easy_2, got {app.summary_metrics['path_cost'].get()!r}"
        )
        for key in ("path_valid", "cost_matches_actions", "terminal_matches_goal"):
            assert app.summary_certificate[key].get() == app._t("cert_pass"), (
                f"cert {key} not pass: {app.summary_certificate[key].get()!r}"
            )
        assert app.notebook.index(app.notebook.select()) == app._tab_indices["tab_summary"], (
            "notebook did not switch to summary tab after _on_run"
        )

        # Trace tab (cụm 4a)
        for attr in ("trace_status_var", "trace_tree"):
            assert hasattr(app, attr), f"trace widget missing: {attr}"
        trace_rows = app.trace_tree.get_children()
        assert len(trace_rows) > 0, "BFS on easy_2 should produce at least one trace row"
        status_text = app.trace_status_var.get()
        assert status_text.endswith("rows") and not status_text.startswith(app._t("trace_idle")), (
            f"trace status not refreshed, got {status_text!r}"
        )
        assert str(len(trace_rows)) in status_text, (
            f"trace status should mention row count, got {status_text!r}"
        )

        # Heuristics tab (cụm 4b)
        for attr in ("heuristics_status_var", "heuristics_totals", "heuristics_tree"):
            assert hasattr(app, attr), f"heuristics widget missing: {attr}"
        assert len(app.heuristics_totals) == 3, "expected 3 heuristic total rows"
        h_status = app.heuristics_status_var.get()
        # easy_2 is 2 moves from goal; BFS selected heuristic defaults to "misplaced" = 2.
        assert "=" in h_status, f"heuristics status not refreshed, got {h_status!r}"
        h_tree_rows = app.heuristics_tree.get_children()
        assert len(h_tree_rows) == 8, (
            f"expected 8 tile rows (tiles 1-8), got {len(h_tree_rows)}"
        )

        # Path playback (cụm 5)
        for attr in (
            "playback_cells", "playback_status_var", "playback_action_var",
            "_playback_path", "_playback_index",
        ):
            assert hasattr(app, attr), f"playback widget missing: {attr}"
        assert len(app.playback_cells) == 9, "playback board should have 9 cells"
        # After BFS on easy_2, path has 3 states (start, mid, goal) → step 0/2
        assert len(app._playback_path) == 3, (
            f"expected 3 path states, got {len(app._playback_path)}"
        )
        assert app._playback_index == 0, "playback should reset to step 0"
        # Step through the path with the public step_playback API
        from eight_puzzle_tk.playback import step_playback
        step_playback(app, "next")
        assert app._playback_index == 1, "playback next did not advance"
        step_playback(app, "last")
        assert app._playback_index == 2, "playback last did not jump to end"
        step_playback(app, "prev")
        assert app._playback_index == 1, "playback prev did not step back"
        step_playback(app, "first")
        assert app._playback_index == 0, "playback first did not jump to start"
        # Board should show numbers (not "-") for populated steps
        assert app.playback_cells[0].cget("text") != "-", (
            "playback board not rendered after run"
        )

        # Compare tab widgets (cụm 5)
        for attr in ("compare_tree", "compare_status_var", "compare_group_var"):
            assert hasattr(app, attr), f"compare widget missing: {attr}"
        assert app.compare_group_var.get() == app.group_var.get(), (
            "compare tab group should default to sidebar group"
        )
        # _on_compare should populate the table and switch to the compare tab
        app._on_compare()
        compare_rows = app.compare_tree.get_children()
        assert len(compare_rows) >= 1, (
            f"compare should produce at least 1 row, got {len(compare_rows)}"
        )
        assert app.notebook.index(app.notebook.select()) == app._tab_indices["tab_compare"], (
            "notebook did not switch to compare tab after _on_compare"
        )
        c_status = app.compare_status_var.get()
        assert str(len(compare_rows)) in c_status, (
            f"compare status should mention count, got {c_status!r}"
        )

        # Error path: _show_run_error must surface the message in the Summary tab
        app._show_run_error("synthetic test error")
        assert app.summary_error_var.get() == "synthetic test error", (
            "error message not propagated to summary tab"
        )
        assert app.trace_status_var.get() == app._t("trace_idle"), (
            "trace tab not reset to idle on error"
        )
        assert app.trace_tree.get_children() == (), (
            "trace tree not cleared on error"
        )
        assert app.heuristics_status_var.get() == app._t("heuristics_idle"), (
            "heuristics tab not reset to idle on error"
        )
        assert app._playback_path == [], "playback path not cleared on error"
        assert app.playback_status_var.get() == app._t("playback_idle"), (
            "playback not reset to idle on error"
        )
        assert app.last_result is None, "last_result not cleared on error"
        assert app.report_status_var.get() == app._t("report_idle"), (
            "report tab not reset to idle on error"
        )

        # Re-run a successful search so the Report tab has data to build on
        app.preset_var.set("easy_2")
        app._on_preset_change()
        app.algorithm_var.set("A*")
        app._on_run()
        assert app.last_result is not None, "last_result not stored after _on_run"
        assert app.last_certificate is not None, "last_certificate missing"
        assert app.last_heuristic == app.heuristic_var.get(), "last_heuristic mismatch"

        # Experiment tab (cụm 6)
        for attr in (
            "experiment_tree", "experiment_status_var", "experiment_baseline_var",
        ):
            assert hasattr(app, attr), f"experiment widget missing: {attr}"
        app._on_experiment_run()
        exp_rows = app.experiment_tree.get_children()
        assert len(exp_rows) > 0, "experiment should produce at least 1 row"
        exp_status = app.experiment_status_var.get()
        assert str(len(exp_rows)) in exp_status or "presets" in exp_status, (
            f"experiment status not refreshed, got {exp_status!r}"
        )
        assert app.experiment_baseline_var.get() != "-", "baseline not populated"

        # Report tab (cụm 6)
        for attr in ("report_text", "report_status_var", "report_last_pack"):
            assert hasattr(app, attr), f"report widget missing: {attr}"
        # Report with no pack → save/copy should show no-pack message
        app._on_report_save()
        assert app.report_status_var.get() == app._t("report_no_pack"), (
            "save without pack should show report_no_pack"
        )
        app._on_report_copy()
        assert app.report_status_var.get() == app._t("report_no_pack"), (
            "copy without pack should show report_no_pack"
        )
        # Build the pack
        app._on_report_generate()
        assert app.report_last_pack is not None, "report pack not stored"
        pack = app.report_last_pack
        assert "markdown" in pack and len(pack["markdown"]) > 100, (
            f"pack markdown too short: {len(pack.get('markdown', ''))} chars"
        )
        # Text widget should contain the markdown
        preview_text = app.report_text.get("1.0", tk.END)
        assert "8-Puzzle" in preview_text or "PEAS" in preview_text, (
            "report preview should contain expected sections"
        )
        # Copy should succeed (clipboard receives text)
        app._on_report_copy()
        clipboard = app.root.clipboard_get()
        assert len(clipboard) > 100, "clipboard should contain the markdown"

        # Vacuum-cleaner game + graph-coloring CSP tab
        from eight_puzzle_tk.vacuum import (
            auto_clean_vacuum,
            color_vacuum_rooms,
            move_vacuum,
            reset_vacuum,
            room_neighbors,
            suck_current_room,
        )
        reset_vacuum(app)
        assert len(app.vacuum_cells) == 6, "vacuum grid should have 6 rooms"
        assert app.vacuum_dirty, "vacuum reset should create dirty rooms"
        color_vacuum_rooms(app)
        assert app.vacuum_coloring, "graph coloring should assign slots to dirty rooms"
        for room, slot in app.vacuum_coloring.items():
            for neighbor in room_neighbors(room):
                if neighbor in app.vacuum_coloring:
                    assert slot != app.vacuum_coloring[neighbor], (
                        "adjacent dirty rooms share the same graph-color slot"
                    )
        before_pos = app.vacuum_position
        move_vacuum(app, "Right")
        assert app.vacuum_position != before_pos, "vacuum move did not update position"
        app.vacuum_dirty.add(app.vacuum_position)
        suck_current_room(app)
        assert app.vacuum_position not in app.vacuum_dirty, "suck should clean current room"
        auto_clean_vacuum(app)
        assert not app.vacuum_dirty, "auto-clean should clean every room"
    finally:
        root.destroy()

    print("Tkinter self-test passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="8-Puzzle desktop visualizer (Tkinter).")
    parser.add_argument("--self-test", action="store_true", help="Run smoke test, do not launch GUI.")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    from eight_puzzle_tk.app import run
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
