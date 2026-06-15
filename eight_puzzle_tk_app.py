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
