"""Step-through visualization of the solution path returned by an algorithm.

The path playback is appended to the Summary tab via
:func:`build_path_playback_section`. After a successful run, the user can step
through each (state, action) pair with prev/next/first/last buttons.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, List

from eight_puzzle_search_app import SearchResult, State


_CELL_FONT = ("Consolas", 16, "bold")


def _make_board(parent: tk.Misc) -> List[ttk.Label]:
    cells: List[ttk.Label] = []
    for i in range(9):
        lbl = ttk.Label(
            parent, text="-", width=3, anchor=tk.CENTER,
            font=_CELL_FONT, relief=tk.RIDGE, padding=6,
        )
        lbl.grid(row=i // 3, column=i % 3, padx=2, pady=2)
        cells.append(lbl)
    return cells


def build_path_playback_section(parent: tk.Misc, app: Any) -> None:
    """Create the path-playback widgets on ``parent`` and store refs on ``app``."""
    app._i18n_labels["playback_title"] = ttk.Label(
        parent, text=app._t("playback_title"), font=("", 11, "bold"),
    )
    app._i18n_labels["playback_title"].pack(anchor=tk.W, pady=(12, 4))

    body = ttk.Frame(parent)
    body.pack(fill=tk.X, pady=(0, 4))

    board_frame = ttk.LabelFrame(body, text=app._t("playback_state"), padding=8)
    board_frame.pack(side=tk.LEFT, padx=(0, 16))
    app.playback_cells = _make_board(board_frame)

    controls = ttk.Frame(body)
    controls.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    app.playback_status_var = tk.StringVar(value=app._t("playback_idle"))
    ttk.Label(controls, textvariable=app.playback_status_var, font=("", 10, "bold")).pack(anchor=tk.W)

    app.playback_action_var = tk.StringVar(value="")
    ttk.Label(controls, textvariable=app.playback_action_var).pack(anchor=tk.W, pady=(0, 8))

    btn_row = ttk.Frame(controls)
    btn_row.pack(fill=tk.X)
    app._i18n_labels["playback_first"] = ttk.Button(
        btn_row, text="|<<", width=4, command=lambda: step_playback(app, "first"),
    )
    app._i18n_labels["playback_first"].pack(side=tk.LEFT, padx=2)
    app._i18n_labels["playback_prev"] = ttk.Button(
        btn_row, text="<", width=4, command=lambda: step_playback(app, "prev"),
    )
    app._i18n_labels["playback_prev"].pack(side=tk.LEFT, padx=2)
    app._i18n_labels["playback_next"] = ttk.Button(
        btn_row, text=">", width=4, command=lambda: step_playback(app, "next"),
    )
    app._i18n_labels["playback_next"].pack(side=tk.LEFT, padx=2)
    app._i18n_labels["playback_last"] = ttk.Button(
        btn_row, text=">>|", width=4, command=lambda: step_playback(app, "last"),
    )
    app._i18n_labels["playback_last"].pack(side=tk.LEFT, padx=2)

    app._playback_path: List[State] = []
    app._playback_actions: List[str] = []
    app._playback_index: int = 0


def _render_board(cells: List[ttk.Label], state: State) -> None:
    for i, value in enumerate(state):
        cells[i].config(text=str(value))


def populate_path_playback(app: Any, result: SearchResult) -> None:
    """Load the result's path into the playback widgets and reset to step 0."""
    app._playback_path = list(result.path)
    app._playback_actions = list(result.actions)
    app._playback_index = 0
    if not app._playback_path:
        app.playback_status_var.set(app._t("playback_no_path"))
        app.playback_action_var.set("")
        for c in app.playback_cells:
            c.config(text="-")
        return
    _render(app, 0)


def reset_path_playback(app: Any) -> None:
    """Clear playback widgets (used on pre-search errors)."""
    app._playback_path = []
    app._playback_actions = []
    app._playback_index = 0
    for c in app.playback_cells:
        c.config(text="-")
    app.playback_status_var.set(app._t("playback_idle"))
    app.playback_action_var.set("")


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
