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
from .academic import build_academic_card
from .theme import PALETTE

CELL_FONT = ("Consolas", 24, "bold")
SECTION_FONT = ("Segoe UI", 10, "bold")
ENTRY_INVALID_BG = "#fee"


class MatrixEditor(ttk.Frame):
    """3x3 state editor that can also behave like a playable 8-puzzle board."""

    SIZE = 3

    def __init__(
        self,
        parent: tk.Misc,
        *,
        initial: State = GOAL_STATE,
        interactive: bool = False,
        show_manual_entry: bool = True,
        on_change: Optional[Callable[[Optional[State]], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self.interactive = interactive
        self._state: State = parse_state(initial)
        self._buttons: List[tk.Button] = []
        self._manual_updating = False

        board = ttk.Frame(self, style="Card.TFrame")
        board.pack(anchor=tk.CENTER)
        for i in range(self.SIZE * self.SIZE):
            btn = tk.Button(
                board,
                text="",
                width=4,
                height=2,
                font=CELL_FONT,
                relief=tk.RAISED,
                bd=1,
                cursor="hand2" if interactive else "arrow",
                command=lambda idx=i: self._on_tile_click(idx),
            )
            btn.grid(row=i // self.SIZE, column=i % self.SIZE, padx=5, pady=5, sticky="nsew")
            self._buttons.append(btn)

        self.manual_var = tk.StringVar()
        if show_manual_entry:
            manual = ttk.Frame(self, style="Card.TFrame")
            manual.pack(fill=tk.X, pady=(8, 0))
            self.manual_entry = ttk.Entry(manual, textvariable=self.manual_var, width=24)
            self.manual_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.manual_entry.bind("<Return>", lambda _event: self.apply_manual_state())
            self.manual_entry.bind("<FocusOut>", lambda _event: self.apply_manual_state())
            ttk.Button(manual, text="Apply", command=self.apply_manual_state).pack(side=tk.LEFT, padx=(6, 0))
        else:
            self.manual_entry = None

        hint = "Click tile next to 0 to move" if interactive else "Goal board"
        self.status_var = tk.StringVar(value=hint)
        ttk.Label(self, textvariable=self.status_var, style="Muted.TLabel").pack(anchor=tk.CENTER, pady=(4, 0))
        self._render()

    def get_state(self) -> Optional[State]:
        try:
            state = parse_state(self.manual_var.get() or self._state)
            validate_state(state)
            return state
        except Exception:
            return None

    def set_state(self, state: State) -> None:
        self._state = parse_state(state)
        self._render()

    def apply_manual_state(self) -> None:
        """Apply the manual text field into the visual board."""
        if self._manual_updating:
            return
        try:
            self._state = parse_state(self.manual_var.get())
        except Exception:
            self.status_var.set("Invalid: need 0-8 exactly once")
            self._flash_invalid()
            if self._on_change:
                self._on_change(None)
            return
        self.status_var.set("State applied")
        self._render(update_manual=False)
        self._emit_change()

    def _on_tile_click(self, idx: int) -> None:
        if not self.interactive:
            return
        blank = self._state.index(0)
        if not self._are_adjacent(idx, blank):
            self.status_var.set("Choose a tile next to 0")
            return
        values = list(self._state)
        values[blank], values[idx] = values[idx], values[blank]
        self._state = tuple(values)  # type: ignore[assignment]
        self.status_var.set(f"Moved tile {values[blank]}")
        self._render()
        self._emit_change()

    def _render(self, *, update_manual: bool = True) -> None:
        for i, value in enumerate(self._state):
            is_blank = value == 0
            self._buttons[i].configure(
                text="0" if is_blank else str(value),
                fg=PALETTE["primary"] if is_blank else PALETTE["text"],
                bg="#e0f2fe" if is_blank else "#ffffff",
                activebackground=PALETTE["cell_hover"],
                activeforeground=PALETTE["text"],
            )
        if update_manual:
            self._manual_updating = True
            self.manual_var.set(" ".join(str(v) for v in self._state))
            self._manual_updating = False

    def _emit_change(self) -> None:
        if self._on_change:
            self._on_change(self.get_state())

    def _flash_invalid(self) -> None:
        for btn in self._buttons:
            btn.configure(bg=ENTRY_INVALID_BG)
        self.after(350, self._render)

    @staticmethod
    def _are_adjacent(a: int, b: int) -> bool:
        ar, ac = divmod(a, MatrixEditor.SIZE)
        br, bc = divmod(b, MatrixEditor.SIZE)
        return abs(ar - br) + abs(ac - bc) == 1


def build_sidebar(parent: tk.Misc, app: Any) -> None:
    """Build the sidebar: preset, scramble, algorithm selectors, limits, action buttons."""
    # Preset section
    app._i18n_labels["section_matrix"] = ttk.Label(
        parent, text=app._t("section_matrix"), font=SECTION_FONT, style="SidebarHeading.TLabel",
    )
    app._i18n_labels["section_matrix"].pack(anchor=tk.W, pady=(8, 2))

    # Preset combobox
    row = ttk.Frame(parent, style="Sidebar.TFrame")
    row.pack(fill=tk.X, pady=(0, 2))
    app._i18n_labels["preset"] = ttk.Label(row, text=app._t("preset"), style="Sidebar.TLabel")
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
    row = ttk.Frame(parent, style="Sidebar.TFrame")
    row.pack(fill=tk.X, pady=(2, 2))
    app._i18n_labels["scramble_moves"] = ttk.Label(row, text=app._t("scramble_moves"), style="Sidebar.TLabel")
    app._i18n_labels["scramble_moves"].pack(side=tk.LEFT)
    app.scramble_var = tk.StringVar(value="20")
    ttk.Spinbox(row, textvariable=app.scramble_var, from_=1, to=200, width=6).pack(side=tk.LEFT, padx=4)

    # Seed
    row = ttk.Frame(parent, style="Sidebar.TFrame")
    row.pack(fill=tk.X, pady=(2, 4))
    app._i18n_labels["seed"] = ttk.Label(row, text=app._t("seed"), style="Sidebar.TLabel")
    app._i18n_labels["seed"].pack(side=tk.LEFT)
    app.seed_var = tk.StringVar(value="")
    ttk.Entry(row, textvariable=app.seed_var, width=10).pack(side=tk.LEFT, padx=4)

    # Shuffle button
    app._i18n_labels["shuffle"] = ttk.Button(
        parent, text=app._t("shuffle"), command=app._on_shuffle, style="Danger.TButton",
    )
    app._i18n_labels["shuffle"].pack(fill=tk.X, pady=(2, 8))

    # Algorithm section
    app._i18n_labels["section_algorithm"] = ttk.Label(
        parent, text=app._t("section_algorithm"), font=SECTION_FONT, style="SidebarHeading.TLabel",
    )
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
    app._i18n_labels["section_heuristic"] = ttk.Label(
        parent, text=app._t("section_heuristic"), font=SECTION_FONT, style="SidebarHeading.TLabel",
    )
    app._i18n_labels["section_heuristic"].pack(anchor=tk.W, pady=(4, 2))
    app.heuristic_var = tk.StringVar(value=DEFAULT_HEURISTICS[0])
    app.heuristic_combo = ttk.Combobox(parent, textvariable=app.heuristic_var, values=DEFAULT_HEURISTICS, state="readonly")
    app.heuristic_combo.pack(fill=tk.X, pady=(0, 4))

    # Limits
    app._i18n_labels["section_limits"] = ttk.Label(
        parent, text=app._t("section_limits"), font=SECTION_FONT, style="SidebarHeading.TLabel",
    )
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
        row = ttk.Frame(parent, style="Sidebar.TFrame")
        row.pack(fill=tk.X, pady=(1, 1))
        app._i18n_labels[key] = ttk.Label(row, text=app._t(key), style="Sidebar.TLabel")
        app._i18n_labels[key].pack(side=tk.LEFT)
        var = tk.StringVar(value=str(default))
        app.limit_vars[key] = var
        ttk.Spinbox(row, textvariable=var, from_=1, to=100000, width=8).pack(side=tk.LEFT, padx=4)

    # Action buttons (also kept as direct attrs for self-test + future enable/disable)
    app.run = ttk.Button(parent, text=app._t("run"), command=app._on_run, style="Run.TButton")
    app._i18n_labels["run"] = app.run
    app.run.pack(fill=tk.X, pady=(12, 2))
    app.compare_all = ttk.Button(parent, text=app._t("compare_all"), command=app._on_compare, style="Primary.TButton")
    app._i18n_labels["compare_all"] = app.compare_all
    app.compare_all.pack(fill=tk.X, pady=(2, 2))


def build_main_area(parent: tk.Misc, app: Any) -> None:
    """Build the main area: Start/Goal matrices on top, Notebook tabs below."""
    header = ttk.Frame(parent, style="TFrame")
    header.pack(fill=tk.X, pady=(0, 12))
    ttk.Label(header, text="AI SEARCH VISUALIZER", style="SidebarHeading.TLabel").pack(anchor=tk.W)
    ttk.Label(header, text="8-Puzzle Search Lab", style="PageTitle.TLabel").pack(anchor=tk.W)
    ttk.Label(
        header,
        text="Chơi trực tiếp trên Start board, rồi chạy thuật toán để xem Node / Frontier / Reached.",
        foreground=PALETTE["muted"],
        wraplength=900,
    ).pack(anchor=tk.W, pady=(2, 0))

    matrices = ttk.Frame(parent, style="Card.TFrame", padding=10)
    matrices.pack(fill=tk.X, pady=(0, 8))

    # Start matrix
    start_frame = ttk.LabelFrame(matrices, text=app._t("start_state"), padding=8)
    start_frame.pack(side=tk.LEFT, padx=(0, 16))
    initial_start = generate_random_state(scramble_moves=5, seed=42)
    app.start_editor = MatrixEditor(start_frame, initial=initial_start, interactive=True)
    app.start_editor.pack()

    # Goal matrix
    goal_frame = ttk.LabelFrame(matrices, text=app._t("goal_state"), padding=8)
    goal_frame.pack(side=tk.LEFT)
    app.goal_editor = MatrixEditor(goal_frame, initial=GOAL_STATE, interactive=False)
    app.goal_editor.pack()

    academic_frame = ttk.Frame(matrices, style="Card.TFrame", padding=(18, 0, 0, 0))
    academic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    build_academic_card(academic_frame, app)

    from .results import build_summary_tab
    from .trace import build_trace_tab
    from .heuristics import build_heuristics_tab
    from .compare import build_compare_tab
    from .playback import build_path_playback_section
    from .experiment import build_experiment_tab
    from .report import build_report_tab

    app.notebook = ttk.Notebook(parent)
    app.notebook.pack(fill=tk.BOTH, expand=True)
    app._tab_indices: Dict[str, int] = {}
    app.tab_frames: Dict[str, ttk.Frame] = {}
    tab_builders = {
        "tab_summary": build_summary_tab,
        "tab_trace": build_trace_tab,
        "tab_heuristics": build_heuristics_tab,
        "tab_compare": build_compare_tab,
        "tab_experiment": build_experiment_tab,
        "tab_report": build_report_tab,
    }
    tab_post_build = {
        "tab_summary": build_path_playback_section,
    }
    for i, key in enumerate(["tab_summary", "tab_trace", "tab_heuristics", "tab_compare", "tab_experiment", "tab_report"]):
        frame = ttk.Frame(app.notebook, padding=8)
        app.notebook.add(frame, text=app._t(key))
        app._tab_indices[key] = i
        app.tab_frames[key] = frame
        builder = tab_builders.get(key)
        if builder:
            builder(frame, app)
        else:
            ttk.Label(frame, text=f"({app._t('coming_soon')})").pack()
        post = tab_post_build.get(key)
        if post:
            post(frame, app)
