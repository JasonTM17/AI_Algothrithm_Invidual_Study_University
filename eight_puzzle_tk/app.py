"""Tkinter App class — orchestrates layout, language toggle, and callbacks.

The App delegates Tkinter widget construction to :mod:`widgets`. Result rendering
(Summary, Trace, Heuristics, Experiment, Report tabs) is wired in later commits.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

from eight_puzzle_search_app import (
    DEMO_PRESETS,
    GOAL_STATE,
    State,
    TraceConfig,
    algorithms_by_group,
    generate_random_state,
    run_algorithm,
    validate_result,
)

from .i18n import DEFAULT_LANG, t
from .theme import apply_theme
from .widgets import build_main_area, build_sidebar


class App:
    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.lang: str = DEFAULT_LANG
        self.root = root or tk.Tk()
        self.root.title(self._t("app_title"))
        self.root.geometry("1200x760")
        self.root.minsize(1100, 680)
        apply_theme(self.root)
        self._i18n_labels: Dict[str, Any] = {}
        self.last_result = None
        self.last_certificate: Optional[Dict[str, Any]] = None
        self.last_heuristic: Optional[str] = None
        self.game_move_count = 0
        self.game_initial_state: State = GOAL_STATE
        self._auto_play_after_id: Optional[str] = None
        self._auto_play_path: list[State] = []
        self._auto_play_actions: list[str] = []
        self._build_layout()
        self._refresh_algorithm_combo()
        self._update_game_panel()

    def _t(self, key: str) -> str:
        return t(key, self.lang)

    def _build_layout(self) -> None:
        self.sidebar = ttk.Frame(self.root, padding=14, style="Sidebar.TFrame")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Separator(self.root, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)
        self.main_area = ttk.Frame(self.root, padding=16, style="TFrame")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_language_toggle()
        build_sidebar(self.sidebar, self)
        build_main_area(self.main_area, self)

    def _build_language_toggle(self) -> None:
        bar = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        bar.pack(fill=tk.X, pady=(0, 8))
        self._i18n_labels["language"] = ttk.Label(bar, text=self._t("language"), style="Sidebar.TLabel")
        self._i18n_labels["language"].pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.lang)
        self._i18n_labels["lang_vi"] = ttk.Radiobutton(
            bar, text=self._t("lang_vi"), value="vi", variable=self.lang_var, command=self._on_lang_change,
        )
        self._i18n_labels["lang_vi"].pack(side=tk.LEFT, padx=4)
        self._i18n_labels["lang_en"] = ttk.Radiobutton(
            bar, text=self._t("lang_en"), value="en", variable=self.lang_var, command=self._on_lang_change,
        )
        self._i18n_labels["lang_en"].pack(side=tk.LEFT, padx=4)

    # --- language change -------------------------------------------------

    def _on_lang_change(self) -> None:
        self.lang = self.lang_var.get()
        for key, widget in self._i18n_labels.items():
            try:
                widget.config(text=self._t(key))
            except tk.TclError:
                pass
        # Preset combobox display values change between languages
        old = self.preset_var.get()
        self.preset_display = [self._t("preset_custom")] + self.preset_keys
        self.preset_combo.config(values=self.preset_display)
        if old not in self.preset_display:
            self.preset_var.set(self.preset_display[0])
        # Notebook tab labels
        for key, idx in self._tab_indices.items():
            self.notebook.tab(idx, text=self._t(key))
        self.root.title(self._t("app_title"))
        self._update_game_panel()

    # --- sidebar callbacks ----------------------------------------------

    def _refresh_algorithm_combo(self) -> None:
        group = self.group_var.get()
        algos = algorithms_by_group().get(group, [])
        self.algorithm_combo.config(values=algos)
        if algos:
            self.algorithm_var.set(algos[0])

    def _on_preset_change(self, _event: Optional[tk.Event] = None) -> None:
        choice = self.preset_var.get()
        if choice == self._t("preset_custom"):
            return
        preset = DEMO_PRESETS.get(choice)
        if preset is not None:
            self._load_game_state(preset)

    def _on_shuffle(self) -> None:
        try:
            moves = int(self.scramble_var.get())
        except ValueError:
            moves = 20
        seed_str = self.seed_var.get().strip()
        seed = int(seed_str) if seed_str else None
        state = generate_random_state(scramble_moves=moves, seed=seed)
        self._load_game_state(state)
        self.preset_var.set(self._t("preset_custom"))

    def _on_group_change(self, _event: Optional[tk.Event] = None) -> None:
        self._refresh_algorithm_combo()
        if hasattr(self, "compare_group_var"):
            self.compare_group_var.set(self.group_var.get())

    def _on_run(self) -> None:
        """Run the selected algorithm and render the result into the Summary tab."""
        start = self.start_editor.get_state()
        goal = self.goal_editor.get_state()
        if start is None or goal is None:
            self._show_run_error(self._t("state_invalid"))
            return
        try:
            cfg = TraceConfig(**{k: int(v.get()) for k, v in self.limit_vars.items()})
        except (TypeError, ValueError) as exc:
            self._show_run_error(f"limits_invalid: {exc}")
            return
        algo = self.algorithm_var.get()
        heur = self.heuristic_var.get()
        try:
            result = run_algorithm(start, algo, heuristic=heur, config=cfg, goal=goal)
            certificate = validate_result(result, heur, goal)
        except Exception as exc:
            self._show_run_error(f"run_failed ({type(exc).__name__}): {exc}")
            return
        from .heuristics import populate_heuristics_tab
        from .playback import populate_path_playback
        from .results import populate_summary
        from .trace import populate_trace_tab

        populate_summary(self, result, certificate)
        populate_trace_tab(self, result)
        populate_heuristics_tab(self, start, goal, heur)
        populate_path_playback(self, result)
        self.last_result = result
        self.last_certificate = certificate
        self.last_heuristic = heur
        self.notebook.select(self._tab_indices["tab_summary"])

    # --- playable board callbacks --------------------------------------

    def _load_game_state(self, state: State) -> None:
        """Load a new puzzle as a fresh playable game."""
        self._stop_auto_play()
        self.game_initial_state = state
        self.game_move_count = 0
        self.start_editor.set_state(state)
        self._update_game_panel(self._t("game_loaded"))

    def _on_game_state_change(self, _state: Optional[State]) -> None:
        self._update_game_panel()

    def _on_player_move(self, tile: int, _state: State) -> None:
        self._stop_auto_play()
        self.game_move_count += 1
        self._update_game_panel(self._t("game_moved").format(tile=tile))

    def _on_game_reset(self) -> None:
        self._load_game_state(self.game_initial_state)

    def _on_game_hint(self) -> None:
        result = self._solve_game_from_current()
        if result is None:
            return
        if not result.found or len(result.path) < 2:
            self.game_hint_var.set(self._t("game_no_hint"))
            return
        action = result.actions[0]
        self.game_hint_var.set(
            self._t("game_hint_value").format(action=action, cost=result.path_cost)
        )

    def _on_game_next_step(self) -> None:
        result = self._solve_game_from_current()
        if result is None:
            return
        if not result.found or len(result.path) < 2:
            self.game_hint_var.set(self._t("game_no_hint"))
            return
        self.game_move_count += 1
        self.start_editor.set_state(result.path[1])
        self._update_game_panel(
            self._t("game_ai_step").format(action=result.actions[0])
        )

    def _on_game_auto_solve(self) -> None:
        self._stop_auto_play()
        result = self._solve_game_from_current()
        if result is None:
            return
        if not result.found or len(result.path) < 2:
            self.game_hint_var.set(self._t("game_no_hint"))
            return
        self._auto_play_path = list(result.path[1:])
        self._auto_play_actions = list(result.actions)
        self.game_hint_var.set(
            self._t("game_auto_ready").format(steps=len(self._auto_play_path))
        )
        self._auto_step()

    def _stop_auto_play(self) -> None:
        if self._auto_play_after_id is not None:
            try:
                self.root.after_cancel(self._auto_play_after_id)
            except tk.TclError:
                pass
        self._auto_play_after_id = None
        self._auto_play_path = []
        self._auto_play_actions = []

    def _auto_step(self) -> None:
        if not self._auto_play_path:
            self._auto_play_after_id = None
            self._update_game_panel(self._t("game_auto_done"))
            return
        next_state = self._auto_play_path.pop(0)
        action = self._auto_play_actions.pop(0) if self._auto_play_actions else "?"
        self.game_move_count += 1
        self.start_editor.set_state(next_state)
        self._update_game_panel(self._t("game_ai_step").format(action=action))
        self._auto_play_after_id = self.root.after(450, self._auto_step)

    def _solve_game_from_current(self):
        start = self.start_editor.get_state()
        goal = self.goal_editor.get_state()
        if start is None or goal is None:
            self.game_hint_var.set(self._t("state_invalid"))
            return None
        try:
            cfg = TraceConfig(max_expansions=50000, max_trace_rows=0)
            result = run_algorithm(start, "A*", heuristic="manhattan", config=cfg, goal=goal)
        except Exception as exc:
            self.game_hint_var.set(f"hint_failed ({type(exc).__name__}): {exc}")
            return None
        if not result.found:
            self.game_hint_var.set(result.message or self._t("game_no_hint"))
        return result

    def _update_game_panel(self, status: Optional[str] = None) -> None:
        if not hasattr(self, "game_moves_var"):
            return
        self.game_moves_var.set(
            self._t("game_moves").format(moves=self.game_move_count)
        )
        start = self.start_editor.get_state() if hasattr(self, "start_editor") else None
        goal = self.goal_editor.get_state() if hasattr(self, "goal_editor") else None
        if start is not None and goal is not None and start == goal:
            self.game_status_var.set(
                self._t("game_solved").format(moves=self.game_move_count)
            )
            return
        self.game_status_var.set(status or self._t("game_ready"))

    def _show_run_error(self, message: str) -> None:
        """Reset the Summary tab to a visible error state without running search."""
        from .heuristics import reset_heuristics_tab
        from .playback import reset_path_playback
        from .report import reset_report_tab
        from .results import show_error_state
        from .trace import reset_trace_tab

        show_error_state(self, message)
        reset_trace_tab(self)
        reset_heuristics_tab(self)
        reset_path_playback(self)
        reset_report_tab(self)
        self.last_result = None
        self.last_certificate = None
        self.last_heuristic = None
        self.notebook.select(self._tab_indices["tab_summary"])

    def _compare_for_group(self, group: str) -> None:
        """Run every algorithm in ``group`` on the current start/goal state."""
        from .compare import compare_for_group
        compare_for_group(self, group)

    def _on_compare(self) -> None:
        """Sidebar 'Compare all' button: run all algorithms in the current group."""
        from .compare import on_compare
        on_compare(self)

    def _on_compare_run(self) -> None:
        """Compare tab 'Run' button: run all algorithms in the tab's selected group."""
        from .compare import on_compare_run
        on_compare_run(self)

    def _on_experiment_run(self) -> None:
        """Experiment tab 'Run' button: run the coursework benchmark suite."""
        from .experiment import on_experiment_run
        on_experiment_run(self)

    def _on_report_generate(self) -> None:
        """Report tab 'Generate' button: build a submission pack from the last run."""
        from .report import on_report_generate
        on_report_generate(self)

    def _on_report_save(self) -> None:
        """Report tab 'Save to file' button: write the Markdown to a user-chosen path."""
        from .report import on_report_save
        on_report_save(self)

    def _on_report_copy(self) -> None:
        """Report tab 'Copy' button: copy the Markdown body to the clipboard."""
        from .report import on_report_copy
        on_report_copy(self)

    # --- lifecycle -------------------------------------------------------

    def start(self) -> None:
        self.root.mainloop()


def run() -> None:
    App().start()


if __name__ == "__main__":
    run()
