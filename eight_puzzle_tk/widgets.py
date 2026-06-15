"""Custom widgets and section builders for the 8-Puzzle Tkinter app.

This module keeps Tkinter-specific layout code out of the App class so the App
stays focused on lifecycle, callbacks, and result handling.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from eight_puzzle_search_app import (
    DEFAULT_HEURISTICS,
    DEMO_PRESETS,
    GOAL_STATE,
    TraceConfig,
    State,
    algorithm_groups,
    algorithms_by_group,
    generate_random_state,
    parse_state,
    validate_state,
)

CELL_FONT = ("Consolas", 18, "bold")
SECTION_FONT = ("", 11, "bold")
ENTRY_INVALID_BG = "#fee"


class MatrixEditor(ttk.Frame):
    """3x3 editable grid representing one 8-puzzle state."""

    SIZE = 3

    def __init__(
        self,
        parent: tk.Misc,
        *,
        initial: State = GOAL_STATE,
        on_change: Optional[Callable[[Optional[State]], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._vars: List[tk.StringVar] = []
        for i in range(self.SIZE * self.SIZE):
            v = tk.StringVar(value=str(initial[i]))
            self._vars.append(v)
            e = ttk.Entry(
                self,
                textvariable=v,
                width=3,
                justify=tk.CENTER,
                font=CELL_FONT,
            )
            e.grid(row=i // self.SIZE, column=i % self.SIZE, padx=2, pady=2, ipady=4)
            v.trace_add("write", lambda *_a, idx=i: self._on_var_changed(idx))

    def get_state(self) -> Optional[State]:
        try:
            raw = tuple(int(v.get()) for v in self._vars)
            state = parse_state(raw)
            validate_state(state)
            return state
        except Exception:
            return None

    def set_state(self, state: State) -> None:
        for i, v in enumerate(state):
            self._vars[i].set(str(v))

    def _on_var_changed(self, _idx: int) -> None:
        if self._on_change:
            self._on_change(self.get_state())


def build_sidebar(parent: tk.Misc, app: Any) -> None:
    """Build the sidebar: preset, scramble, algorithm selectors, limits, action buttons."""
    # Preset section
    app._i18n_labels["section_matrix"] = ttk.Label(parent, text=app._t("section_matrix"), font=SECTION_FONT)
    app._i18n_labels["section_matrix"].pack(anchor=tk.W, pady=(8, 2))

    # Preset combobox
    row = ttk.Frame(parent)
    row.pack(fill=tk.X, pady=(0, 2))
    app._i18n_labels["preset"] = ttk.Label(row, text=app._t("preset"))
    app._i18n_labels["preset"].pack(side=tk.LEFT)
    app.preset_keys = list(DEMO_PRESETS.keys())
    app.preset_display = [app._t("preset_custom")] + app.preset_keys
    app.preset_var = tk.StringVar(value=app.preset_display[0])
    app.preset_combo = ttk.Combobox(
        row, textvariable=app.preset_var, values=app.preset_display, state="readonly", width=18,
    )
    app.preset_combo.pack(side=tk.LEFT, padx=4)
    app.preset_combo.bind("<<ComboboxSelected>>", app._on_preset_change)

    # Scramble moves
    row = ttk.Frame(parent)
    row.pack(fill=tk.X, pady=(2, 2))
    app._i18n_labels["scramble_moves"] = ttk.Label(row, text=app._t("scramble_moves"))
    app._i18n_labels["scramble_moves"].pack(side=tk.LEFT)
    app.scramble_var = tk.StringVar(value="20")
    ttk.Spinbox(row, textvariable=app.scramble_var, from_=1, to=200, width=6).pack(side=tk.LEFT, padx=4)

    # Seed
    row = ttk.Frame(parent)
    row.pack(fill=tk.X, pady=(2, 4))
    app._i18n_labels["seed"] = ttk.Label(row, text=app._t("seed"))
    app._i18n_labels["seed"].pack(side=tk.LEFT)
    app.seed_var = tk.StringVar(value="")
    ttk.Entry(row, textvariable=app.seed_var, width=10).pack(side=tk.LEFT, padx=4)

    # Shuffle button
    app._i18n_labels["shuffle"] = ttk.Button(parent, text=app._t("shuffle"), command=app._on_shuffle)
    app._i18n_labels["shuffle"].pack(fill=tk.X, pady=(2, 8))

    # Algorithm section
    app._i18n_labels["section_algorithm"] = ttk.Label(parent, text=app._t("section_algorithm"), font=SECTION_FONT)
    app._i18n_labels["section_algorithm"].pack(anchor=tk.W, pady=(4, 2))
    app.algorithm_groups_list = algorithm_groups()
    app.group_var = tk.StringVar(value=app.algorithm_groups_list[0])
    app.group_combo = ttk.Combobox(parent, textvariable=app.group_var, values=app.algorithm_groups_list, state="readonly")
    app.group_combo.pack(fill=tk.X, pady=(0, 2))
    app.group_combo.bind("<<ComboboxSelected>>", app._on_group_change)
    app.algorithm_var = tk.StringVar()
    app.algorithm_combo = ttk.Combobox(parent, textvariable=app.algorithm_var, state="readonly")
    app.algorithm_combo.pack(fill=tk.X, pady=(0, 4))

    # Heuristic
    app._i18n_labels["section_heuristic"] = ttk.Label(parent, text=app._t("section_heuristic"), font=SECTION_FONT)
    app._i18n_labels["section_heuristic"].pack(anchor=tk.W, pady=(4, 2))
    app.heuristic_var = tk.StringVar(value=DEFAULT_HEURISTICS[0])
    app.heuristic_combo = ttk.Combobox(parent, textvariable=app.heuristic_var, values=DEFAULT_HEURISTICS, state="readonly")
    app.heuristic_combo.pack(fill=tk.X, pady=(0, 4))

    # Limits
    app._i18n_labels["section_limits"] = ttk.Label(parent, text=app._t("section_limits"), font=SECTION_FONT)
    app._i18n_labels["section_limits"].pack(anchor=tk.W, pady=(4, 2))
    cfg = TraceConfig()
    app.limit_vars: Dict[str, tk.StringVar] = {}
    for key, default in [
        ("max_expansions", cfg.max_expansions),
        ("dfs_depth_limit", cfg.dfs_depth_limit),
        ("ids_max_depth", cfg.ids_max_depth),
        ("ida_max_iterations", cfg.ida_max_iterations),
        ("local_max_steps", cfg.local_max_steps),
        ("random_restarts", cfg.random_restarts),
    ]:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=(1, 1))
        app._i18n_labels[f"limit_{key}"] = ttk.Label(row, text=app._t(key))
        app._i18n_labels[f"limit_{key}"].pack(side=tk.LEFT)
        var = tk.StringVar(value=str(default))
        app.limit_vars[key] = var
        ttk.Spinbox(row, textvariable=var, from_=1, to=100000, width=8).pack(side=tk.LEFT, padx=4)

    # Action buttons (also kept as direct attrs for self-test + future enable/disable)
    app.run = ttk.Button(parent, text=app._t("run"), command=app._on_run)
    app._i18n_labels["run"] = app.run
    app.run.pack(fill=tk.X, pady=(12, 2))
    app.compare_all = ttk.Button(parent, text=app._t("compare_all"), command=app._on_compare)
    app._i18n_labels["compare_all"] = app.compare_all
    app.compare_all.pack(fill=tk.X, pady=(2, 2))


def build_main_area(parent: tk.Misc, app: Any) -> None:
    """Build the main area: Start/Goal matrices on top, Notebook tabs below."""
    matrices = ttk.Frame(parent)
    matrices.pack(fill=tk.X, pady=(0, 8))

    # Start matrix
    start_frame = ttk.LabelFrame(matrices, text=app._t("start_state"), padding=8)
    start_frame.pack(side=tk.LEFT, padx=(0, 16))
    initial_start = generate_random_state(scramble_moves=5, seed=42)
    app.start_editor = MatrixEditor(start_frame, initial=initial_start)
    app.start_editor.pack()

    # Goal matrix
    goal_frame = ttk.LabelFrame(matrices, text=app._t("goal_state"), padding=8)
    goal_frame.pack(side=tk.LEFT)
    app.goal_editor = MatrixEditor(goal_frame, initial=GOAL_STATE)
    app.goal_editor.pack()

    from .results import build_summary_tab
    from .trace import build_trace_tab

    app.notebook = ttk.Notebook(parent)
    app.notebook.pack(fill=tk.BOTH, expand=True)
    app._tab_indices: Dict[str, int] = {}
    app.tab_frames: Dict[str, ttk.Frame] = {}
    tab_builders = {"tab_summary": build_summary_tab, "tab_trace": build_trace_tab}
    for i, key in enumerate(["tab_summary", "tab_trace", "tab_heuristics", "tab_experiment", "tab_report"]):
        frame = ttk.Frame(app.notebook, padding=8)
        app.notebook.add(frame, text=app._t(key))
        app._tab_indices[key] = i
        app.tab_frames[key] = frame
        builder = tab_builders.get(key)
        if builder:
            builder(frame, app)
        else:
            ttk.Label(frame, text=f"({app._t('coming_soon')})").pack()
