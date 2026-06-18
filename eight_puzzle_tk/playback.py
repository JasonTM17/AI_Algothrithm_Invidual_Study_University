"""Step-through visualization of the solution path returned by an algorithm.

The path playback is appended to the Summary tab via
:func:`build_path_playback_section`. After a successful run, the user can step
through each (state, action) pair with prev/next/first/last buttons.

The section is hidden on app startup and shown only when a result with a path
is available.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, List

from eight_puzzle_search_app import SearchResult, State

from .theme import PALETTE


_CELL_FONT = ("Consolas", 36, "bold")


def _make_board(parent: tk.Misc) -> List[tk.Label]:
    """Build a 3x3 grid of bordered Labels for step playback."""
    # Wrap each cell in a border frame so the grid has clean separation.
    border = tk.Frame(parent, bg=PALETTE["border"], bd=0)
    border.pack(anchor=tk.CENTER, padx=4, pady=4)
    cells: List[tk.Label] = []
    inner = tk.Frame(border, bg=PALETTE["border"], bd=0)
    inner.pack(padx=3, pady=3)
    for i in range(9):
        lbl = tk.Label(
            inner, text="-", width=4, height=1,
            font=_CELL_FONT, relief=tk.FLAT, borderwidth=0,
            bg=PALETTE["tile_bg"], fg=PALETTE["text"],
        )
        lbl.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="nsew")
        cells.append(lbl)
    for r in range(3):
        inner.rowconfigure(r, weight=1, uniform="cell", minsize=70)
    for c in range(3):
        inner.columnconfigure(c, weight=1, uniform="cell", minsize=70)
    return cells


def build_path_playback_section(parent: tk.Misc, app: Any) -> None:
    """Create path-playback widgets on ``parent`` and store refs on ``app``.

    The section is created hidden (not packed). It is shown when
    :func:`populate_path_playback` loads a result with a non-empty path,
    and hidden again by :func:`reset_path_playback`.
    """
    # Container for the entire playback section — hidden until a result exists.
    app.playback_container = ttk.LabelFrame(
        parent, text=app._t("playback_title"), padding=12,
    )

    body = ttk.Frame(app.playback_container)
    body.pack(fill=tk.X, pady=(0, 8))

    board_frame = ttk.LabelFrame(body, text=app._t("playback_state"), padding=10)
    board_frame.pack(side=tk.LEFT, padx=(0, 20), anchor=tk.N)
    app.playback_cells = _make_board(board_frame)

    controls = tk.Frame(app.playback_container, bg=PALETTE["card_bg"])
    controls.pack(fill=tk.X, pady=(8, 0))

    app.playback_status_var = tk.StringVar(value=app._t("playback_idle"))
    tk.Label(
        controls, textvariable=app.playback_status_var,
        font=("Segoe UI", 10, "bold"), bg=PALETTE["card_bg"], fg=PALETTE["text"],
    ).pack(anchor=tk.W)

    app.playback_action_var = tk.StringVar(value="")
    tk.Label(
        controls, textvariable=app.playback_action_var,
        font=("Segoe UI", 10), bg=PALETTE["card_bg"], fg=PALETTE["muted"],
    ).pack(anchor=tk.W, pady=(0, 8))

    btn_row = ttk.Frame(controls)
    btn_row.pack(fill=tk.X)
    app._i18n_labels["playback_first"] = ttk.Button(
        btn_row, text=app._t("playback_first"), command=lambda: step_playback(app, "first"),
    )
    app._i18n_labels["playback_first"].pack(side=tk.LEFT, padx=2)
    app._i18n_labels["playback_prev"] = ttk.Button(
        btn_row, text=app._t("playback_prev"), command=lambda: step_playback(app, "prev"),
    )
    app._i18n_labels["playback_prev"].pack(side=tk.LEFT, padx=2)
    app._i18n_labels["playback_next"] = ttk.Button(
        btn_row, text=app._t("playback_next"), command=lambda: step_playback(app, "next"),
    )
    app._i18n_labels["playback_next"].pack(side=tk.LEFT, padx=2)
    app._i18n_labels["playback_last"] = ttk.Button(
        btn_row, text=app._t("playback_last"), command=lambda: step_playback(app, "last"),
    )
    app._i18n_labels["playback_last"].pack(side=tk.LEFT, padx=2)

    app._playback_path: List[State] = []
    app._playback_actions: List[str] = []
    app._playback_index: int = 0


def _render_board(cells: List[tk.Label], state: State) -> None:
    for i, value in enumerate(state):
        is_blank = value == 0
        cells[i].config(
            text="" if is_blank else str(value),
            bg=PALETTE["blank_tile_bg"] if is_blank else PALETTE["tile_bg"],
            fg=PALETTE["blank_tile_fg"] if is_blank else PALETTE["text"],
        )


def populate_path_playback(app: Any, result: SearchResult) -> None:
    """Load the result's path into the playback widgets and reset to step 0.

    Shows the playback section only when a non-empty path is available.
    """
    app._playback_path = list(result.path)
    app._playback_actions = list(result.actions)
    app._playback_index = 0
    if not app._playback_path:
        app.playback_status_var.set(app._t("playback_no_path"))
        app.playback_action_var.set("")
        for c in app.playback_cells:
            c.config(text="-")
        app.playback_container.pack_forget()
        return
    # Show the playback section now that a path exists
    if not app.playback_container.winfo_ismapped():
        app.playback_container.pack(fill=tk.X, pady=(10, 0))
    _render(app, 0)
    # Auto-scroll the ScrolledFrame to show the playback board.
    try:
        scrolled = app.notebook.nametowidget(
            app.notebook.tabs()[app._tab_indices.get("tab_summary", 0)]
        )
        if hasattr(scrolled, "canvas"):
            scrolled.canvas.update_idletasks()
            bbox = scrolled.canvas.bbox("all")
            if bbox:
                # Scroll to the bottom so playback is visible
                scrolled.canvas.yview_moveto(1.0)
    except Exception:
        pass


def reset_path_playback(app: Any) -> None:
    """Clear playback widgets and hide the section (used on pre-search errors)."""
    app._playback_path = []
    app._playback_actions = []
    app._playback_index = 0
    for c in app.playback_cells:
        c.config(text="-")
    app.playback_status_var.set(app._t("playback_idle"))
    app.playback_action_var.set("")
    app.playback_container.pack_forget()


def step_playback(app: Any, direction: str) -> None:
    """Move the playback cursor; called by prev/next/first/last buttons."""
    if not app._playback_path:
        return
    last = len(app._playback_path) - 1
    if direction == "first":
        app._playback_index = 0
    elif direction == "last":
        app._playback_index = last
    elif direction == "prev":
        app._playback_index = max(0, app._playback_index - 1)
    elif direction == "next":
        app._playback_index = min(last, app._playback_index + 1)
    _render(app, app._playback_index)


def _render(app: Any, index: int) -> None:
    state = app._playback_path[index]
    _render_board(app.playback_cells, state)
    if index == 0:
        action_text = app._t("playback_action_start")
    else:
        action_text = f"{index}. {app._playback_actions[index - 1]}"
    app.playback_action_var.set(action_text)
    total = len(app._playback_path) - 1
    app.playback_status_var.set(
        app._t("playback_step").format(step=index, total=total)
    )
