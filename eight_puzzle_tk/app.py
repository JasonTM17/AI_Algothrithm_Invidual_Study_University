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
from .widgets import build_main_area, build_sidebar


class App:
    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.lang: str = DEFAULT_LANG
        self.root = root or tk.Tk()
        self.root.title(self._t("app_title"))
        self.root.geometry("1280x820")
        self.root.minsize(1024, 720)
        self._i18n_labels: Dict[str, Any] = {}
        self._build_layout()
        self._refresh_algorithm_combo()

    def _t(self, key: str) -> str:
        return t(key, self.lang)

    def _build_layout(self) -> None:
        self.sidebar = ttk.Frame(self.root, padding=8)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.main_area = ttk.Frame(self.root, padding=8)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._build_language_toggle()
        build_sidebar(self.sidebar, self)
        build_main_area(self.main_area, self)

    def _build_language_toggle(self) -> None:
        bar = ttk.Frame(self.sidebar)
        bar.pack(fill=tk.X, pady=(0, 8))
        self._i18n_labels["language"] = ttk.Label(bar, text=self._t("language"))
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
            self.start_editor.set_state(preset)

    def _on_shuffle(self) -> None:
        try:
            moves = int(self.scramble_var.get())
        except ValueError:
            moves = 20
        seed_str = self.seed_var.get().strip()
        seed = int(seed_str) if seed_str else None
        state = generate_random_state(scramble_moves=moves, seed=seed)
        self.start_editor.set_state(state)
        self.preset_var.set(self._t("preset_custom"))

    def _on_group_change(self, _event: Optional[tk.Event] = None) -> None:
        self._refresh_algorithm_combo()

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
        from .results import populate_summary
        from .trace import populate_trace_tab

        populate_summary(self, result, certificate)
        populate_trace_tab(self, result)
        self.notebook.select(self._tab_indices["tab_summary"])

    def _show_run_error(self, message: str) -> None:
        """Reset the Summary tab to a visible error state without running search."""
        from .results import show_error_state
        from .trace import reset_trace_tab

        show_error_state(self, message)
        reset_trace_tab(self)
        self.notebook.select(self._tab_indices["tab_summary"])

    def _on_compare(self) -> None:
        # Wired in cụm 3 (compare all algorithms).
        pass

    # --- lifecycle -------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()


def run() -> None:
    App().run()


if __name__ == "__main__":
    run()
