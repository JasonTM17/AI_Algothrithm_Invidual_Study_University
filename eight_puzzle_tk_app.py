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
        assert len(app._tab_indices) == 5, "notebook should have 5 tabs"

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
