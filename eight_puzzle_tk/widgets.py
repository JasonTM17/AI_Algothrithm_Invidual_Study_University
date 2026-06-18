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

CELL_FONT = ("Consolas", 28, "bold")
SECTION_FONT = ("Segoe UI", 10, "bold")
ENTRY_INVALID_BG = PALETTE["invalid_bg"]


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
        on_move: Optional[Callable[[int, State], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._on_move = on_move
        self.interactive = interactive
        self._state: State = parse_state(initial)
        self._buttons: List[tk.Button] = []
        self._manual_updating = False

        board = tk.Frame(self, bg=PALETTE["border"], bd=0)
        board.pack(anchor=tk.CENTER)
        for col in range(self.SIZE):
            board.columnconfigure(col, weight=1, uniform="cell")
        for row in range(self.SIZE):
            board.rowconfigure(row, weight=1, uniform="cell")
        for i in range(self.SIZE * self.SIZE):
            btn = tk.Button(
                board,
                text="",
                width=3,
                height=1,
                font=CELL_FONT,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2" if interactive else "arrow",
                command=lambda idx=i: self._on_tile_click(idx),
            )
            btn.grid(row=i // self.SIZE, column=i % self.SIZE, padx=2, pady=2, sticky="nsew")
            self._buttons.append(btn)

        self.manual_var = tk.StringVar()
        if show_manual_entry:
            manual = tk.Frame(self, bg=PALETTE["card_bg"])
            manual.pack(fill=tk.X, pady=(10, 0))
            self.manual_entry = ttk.Entry(manual, textvariable=self.manual_var, width=22)
            self.manual_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.manual_entry.bind("<Return>", lambda _event: self.apply_manual_state())
            self.manual_entry.bind("<FocusOut>", lambda _event: self.apply_manual_state())
            ttk.Button(manual, text="Apply", command=self.apply_manual_state).pack(side=tk.LEFT, padx=(6, 0))
        else:
            self.manual_entry = None

        hint = "Click tile next to 0 to move" if interactive else "Goal board"
        self.status_var = tk.StringVar(value=hint)
        tk.Label(self, textvariable=self.status_var, bg=PALETTE["card_bg"],
                 fg=PALETTE["muted"], font=("Segoe UI", 9)).pack(anchor=tk.CENTER, pady=(6, 0))
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
        moved_tile = values[idx]
        values[blank], values[idx] = values[idx], values[blank]
        self._state = tuple(values)  # type: ignore[assignment]
        self.status_var.set(f"Moved tile {moved_tile}")
        self._render()
        if self._on_move:
            self._on_move(moved_tile, self._state)
        self._emit_change()

    def _render(self, *, update_manual: bool = True) -> None:
        for i, value in enumerate(self._state):
            is_blank = value == 0
            self._buttons[i].configure(
                text="0" if is_blank else str(value),
                fg=PALETTE["blank_tile_fg"] if is_blank else PALETTE["text"],
                bg=PALETTE["blank_tile_bg"] if is_blank else PALETTE["tile_bg"],
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


def _sidebar_group(parent: tk.Misc, app: Any, title_key: str) -> ttk.Frame:
    """Create a styled Labelframe group in the sidebar."""
    frame = ttk.LabelFrame(parent, text=app._t(title_key), style="SidebarGroup.TLabelframe", padding=8)
    frame.pack(fill=tk.X, pady=(0, 10))
    return frame


def _sidebar_row(parent: tk.Misc, app: Any, label_key: str) -> ttk.Frame:
    """Create a label + control row inside a sidebar group."""
    row = ttk.Frame(parent, style="Sidebar.TFrame")
    row.pack(fill=tk.X, pady=(2, 2))
    app._i18n_labels[label_key] = ttk.Label(row, text=app._t(label_key), style="Sidebar.TLabel")
    app._i18n_labels[label_key].pack(side=tk.LEFT)
    return row


def build_sidebar(parent: tk.Misc, app: Any) -> None:
    """Build the sidebar: preset, scramble, algorithm selectors, limits, action buttons."""
    # Matrix group
    matrix_group = _sidebar_group(parent, app, "section_matrix")

    row = _sidebar_row(matrix_group, app, "preset")
    app.preset_keys = list(DEMO_PRESETS.keys())
    app.preset_display = [app._t("preset_custom")] + app.preset_keys
    app.preset_var = tk.StringVar(value=app.preset_display[0])
    app.preset_combo = ttk.Combobox(
        row, textvariable=app.preset_var, values=app.preset_display, state="readonly", width=18,
    )
    app.preset_combo.pack(side=tk.LEFT, padx=4)
    app.preset_combo.bind("<<ComboboxSelected>>", app._on_preset_change)

    row = _sidebar_row(matrix_group, app, "scramble_moves")
    app.scramble_var = tk.StringVar(value="20")
    ttk.Spinbox(row, textvariable=app.scramble_var, from_=1, to=200, width=6).pack(side=tk.LEFT, padx=4)

    row = _sidebar_row(matrix_group, app, "seed")
    app.seed_var = tk.StringVar(value="")
    ttk.Entry(row, textvariable=app.seed_var, width=10).pack(side=tk.LEFT, padx=4)

    app._i18n_labels["shuffle"] = ttk.Button(
        matrix_group, text=app._t("shuffle"), command=app._on_shuffle, style="Danger.TButton",
    )
    app._i18n_labels["shuffle"].pack(fill=tk.X, pady=(6, 0))

    # Algorithm group
    algo_group = _sidebar_group(parent, app, "section_algorithm")
    app.algorithm_groups_list = algorithm_groups()
    app.group_var = tk.StringVar(value=app.algorithm_groups_list[0])
    app.group_combo = ttk.Combobox(algo_group, textvariable=app.group_var, values=app.algorithm_groups_list, state="readonly")
    app.group_combo.pack(fill=tk.X, pady=(0, 4))
    app.group_combo.bind("<<ComboboxSelected>>", app._on_group_change)
    app.algorithm_var = tk.StringVar()
    app.algorithm_combo = ttk.Combobox(algo_group, textvariable=app.algorithm_var, state="readonly")
    app.algorithm_combo.pack(fill=tk.X, pady=(0, 2))

    # Heuristic group
    heuristic_group = _sidebar_group(parent, app, "section_heuristic")
    app.heuristic_var = tk.StringVar(value=DEFAULT_HEURISTICS[0])
    app.heuristic_combo = ttk.Combobox(heuristic_group, textvariable=app.heuristic_var, values=DEFAULT_HEURISTICS, state="readonly")
    app.heuristic_combo.pack(fill=tk.X, pady=(0, 2))

    # Limits group
    limits_group = _sidebar_group(parent, app, "section_limits")
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
        row = _sidebar_row(limits_group, app, key)
        var = tk.StringVar(value=str(default))
        app.limit_vars[key] = var
        ttk.Spinbox(row, textvariable=var, from_=1, to=100000, width=8).pack(side=tk.LEFT, padx=4)

    # Action buttons
    app.run = ttk.Button(parent, text=app._t("run"), command=app._on_run, style="Run.TButton")
    app._i18n_labels["run"] = app.run
    app.run.pack(fill=tk.X, pady=(4, 4))
    app.compare_all = ttk.Button(parent, text=app._t("compare_all"), command=app._on_compare, style="Primary.TButton")
    app._i18n_labels["compare_all"] = app.compare_all
    app.compare_all.pack(fill=tk.X, pady=(4, 0))

    # Spacer frame: pushes everything to the top, fills remaining vertical space
    spacer = ttk.Frame(parent, style="Sidebar.TFrame")
    spacer.pack(fill=tk.BOTH, expand=True)


def build_main_area(parent: tk.Misc, app: Any) -> None:
    """Build the main area: Start/Goal matrices on top, Notebook tabs below."""
    header = ttk.Frame(parent, style="TFrame")
    header.pack(fill=tk.X, pady=(0, 12))
    app._i18n_labels["header_subtitle"] = ttk.Label(
        header, text=app._t("header_subtitle"), style="SidebarHeading.TLabel",
    )
    app._i18n_labels["header_subtitle"].pack(anchor=tk.W)
    app._i18n_labels["header_title"] = ttk.Label(
        header, text=app._t("header_title"), style="PageTitle.TLabel",
    )
    app._i18n_labels["header_title"].pack(anchor=tk.W)
    app._i18n_labels["header_description"] = ttk.Label(
        header,
        text=app._t("header_description"),
        foreground=PALETTE["muted"],
        wraplength=900,
    )
    app._i18n_labels["header_description"].pack(anchor=tk.W, pady=(2, 0))

    matrices = tk.Frame(parent, bg=PALETTE["border"])
    matrices.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
    # Distribute width: start smaller, goal smaller, academic gets the most space.
    matrices.columnconfigure(0, weight=2, uniform="mat")  # start
    matrices.columnconfigure(1, weight=2, uniform="mat")  # goal
    matrices.columnconfigure(2, weight=5, uniform="mat")  # academic
    matrices.rowconfigure(0, weight=1)

    # Start matrix
    start_frame = ttk.LabelFrame(matrices, text=app._t("start_state"), padding=10)
    start_frame.grid(row=0, column=0, padx=(0, 2), sticky="nsew")
    initial_start = generate_random_state(scramble_moves=5, seed=42)
    app.start_editor = MatrixEditor(
        start_frame,
        initial=initial_start,
        interactive=True,
        on_change=app._on_game_state_change,
        on_move=app._on_player_move,
    )
    app.start_editor.pack(anchor=tk.N)
    app.game_initial_state = initial_start

    game_panel = ttk.Frame(start_frame, style="Card.TFrame")
    game_panel.pack(fill=tk.X, pady=(8, 0))
    app.game_moves_var = tk.StringVar(value="")
    ttk.Label(game_panel, textvariable=app.game_moves_var, style="CardSubheading.TLabel").pack(anchor=tk.W)
    app.game_status_var = tk.StringVar(value="")
    ttk.Label(game_panel, textvariable=app.game_status_var, style="Muted.TLabel", wraplength=380).pack(anchor=tk.W)
    app.game_hint_var = tk.StringVar(value="")
    ttk.Label(game_panel, textvariable=app.game_hint_var, style="Muted.TLabel", wraplength=380).pack(anchor=tk.W)

    game_buttons = ttk.Frame(start_frame, style="Card.TFrame")
    game_buttons.pack(fill=tk.X, pady=(8, 0))
    app._i18n_labels["game_reset"] = ttk.Button(
        game_buttons, text=app._t("game_reset"), command=app._on_game_reset,
    )
    app._i18n_labels["game_reset"].grid(row=0, column=0, sticky="ew", padx=2, pady=2)
    app._i18n_labels["game_hint"] = ttk.Button(
        game_buttons, text=app._t("game_hint"), command=app._on_game_hint,
    )
    app._i18n_labels["game_hint"].grid(row=0, column=1, sticky="ew", padx=2, pady=2)
    app._i18n_labels["game_next_step"] = ttk.Button(
        game_buttons, text=app._t("game_next_step"), command=app._on_game_next_step,
    )
    app._i18n_labels["game_next_step"].grid(row=1, column=0, sticky="ew", padx=2, pady=2)
    app._i18n_labels["game_auto_solve"] = ttk.Button(
        game_buttons, text=app._t("game_auto_solve"), command=app._on_game_auto_solve,
    )
    app._i18n_labels["game_auto_solve"].grid(row=1, column=1, sticky="ew", padx=2, pady=2)
    for col in (0, 1):
        game_buttons.columnconfigure(col, weight=1)

    # Goal matrix
    goal_frame = ttk.LabelFrame(matrices, text=app._t("goal_state"), padding=10)
    goal_frame.grid(row=0, column=1, padx=2, sticky="nsew")
    app.goal_editor = MatrixEditor(goal_frame, initial=GOAL_STATE, interactive=False)
    app.goal_editor.pack(anchor=tk.N)

    academic_frame = tk.Frame(matrices, bg=PALETTE["card_bg"], padx=14, pady=10)
    academic_frame.grid(row=0, column=2, padx=(2, 0), sticky="nsew")
    academic_frame.columnconfigure(0, weight=1)
    build_academic_card(academic_frame, app)

    from .results import build_summary_tab
    from .trace import build_trace_tab
    from .heuristics import build_heuristics_tab
    from .compare import build_compare_tab
    from .playback import build_path_playback_section
    from .experiment import build_experiment_tab
    from .report import build_report_tab
    from .vacuum import build_vacuum_tab

    app.notebook = ttk.Notebook(parent)
    app.notebook.pack(fill=tk.BOTH, expand=True)
    app._tab_indices: Dict[str, int] = {}
    app.tab_frames: Dict[str, tk.Misc] = {}
    tab_builders = {
        "tab_summary": build_summary_tab,
        "tab_trace": build_trace_tab,
        "tab_heuristics": build_heuristics_tab,
        "tab_compare": build_compare_tab,
        "tab_experiment": build_experiment_tab,
        "tab_vacuum": build_vacuum_tab,
        "tab_report": build_report_tab,
    }
    tab_post_build = {
        "tab_summary": build_path_playback_section,
    }
    for i, key in enumerate([
        "tab_summary",
        "tab_trace",
        "tab_heuristics",
        "tab_compare",
        "tab_experiment",
        "tab_vacuum",
        "tab_report",
    ]):
        from .scrollable import ScrolledFrame
        scroll = ScrolledFrame(app.notebook, bg=PALETTE["card_bg"])
        app.notebook.add(scroll, text=app._t(key))
        frame = scroll.inner
        frame.configure(padding=12)
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
