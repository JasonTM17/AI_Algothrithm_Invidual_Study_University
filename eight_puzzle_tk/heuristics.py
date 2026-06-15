"""Render heuristic breakdown for the current start state into the Heuristics tab.

Uses :func:`eight_puzzle_search_app.explain_heuristic` for tile-level and
total evidence. Shows the selected heuristic's h(start) plus a comparison of
misplaced / manhattan / linear-conflict totals for coursework explanation.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from eight_puzzle_search_app import GOAL_STATE, State, explain_heuristic


_TILE_COLS: tuple = ("Tile", "Current", "Goal", "Misplaced", "Manhattan")
_TOTAL_KEYS: tuple = ("misplaced", "manhattan", "linear_conflict")


def build_heuristics_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Heuristics tab widgets and store references on ``app``."""
    app._i18n_labels["heuristics_title"] = ttk.Label(
        parent, text=app._t("heuristics_title"), font=("", 12, "bold"),
    )
    app._i18n_labels["heuristics_title"].pack(anchor=tk.W, pady=(0, 6))

    app.heuristics_status_var = tk.StringVar(value=app._t("heuristics_idle"))
    ttk.Label(parent, textvariable=app.heuristics_status_var).pack(anchor=tk.W)

    totals_frame = ttk.LabelFrame(parent, text=app._t("heuristics_totals"), padding=8)
    totals_frame.pack(fill=tk.X, pady=(8, 0))
    app.heuristics_totals: dict = {}
    for key in _TOTAL_KEYS:
        row = ttk.Frame(totals_frame)
        row.pack(fill=tk.X, pady=1)
        label_key = f"heuristics_{key}"
        app._i18n_labels[label_key] = ttk.Label(
            row, text=app._t(label_key), width=22, anchor=tk.W,
        )
        app._i18n_labels[label_key].pack(side=tk.LEFT)
        var = tk.StringVar(value="-")
        ttk.Label(row, textvariable=var, anchor=tk.W).pack(side=tk.LEFT, padx=(8, 0))
        app.heuristics_totals[key] = var

    table_frame = ttk.LabelFrame(parent, text=app._t("heuristics_per_tile"), padding=8)
    table_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    tree = ttk.Treeview(table_frame, columns=_TILE_COLS, show="headings", height=8)
    widths = {"Tile": 50, "Current": 90, "Goal": 90, "Misplaced": 90, "Manhattan": 90}
    for col in _TILE_COLS:
        tree.heading(col, text=col)
        tree.column(
            col, width=widths.get(col, 80),
            anchor=tk.E if col in {"Tile", "Misplaced", "Manhattan"} else tk.W,
        )
    app.heuristics_tree = tree
    tree.pack(fill=tk.BOTH, expand=True)

    app.heuristics_note_var = tk.StringVar(value="")
    ttk.Label(
        parent, textvariable=app.heuristics_note_var, wraplength=640, justify=tk.LEFT,
    ).pack(anchor=tk.W, pady=(8, 0))


def populate_heuristics_tab(app: Any, state: State, goal: State, heuristic_name: str) -> None:
    """Refresh the Heuristics tab from :func:`explain_heuristic`."""
    explanation = explain_heuristic(state, heuristic_name, goal)
    app.heuristics_status_var.set(
        f"{explanation['heuristic']} = {explanation['selected_value']}"
    )
    totals = explanation["totals"]
    for key in ("misplaced", "manhattan"):
        app.heuristics_totals[key].set(str(totals.get(key, "-")))
    linear = totals.get("linear_conflict")
    app.heuristics_totals["linear_conflict"].set(
        str(linear) if linear is not None else app._t("heuristics_not_applicable")
    )
    tree = app.heuristics_tree
    tree.delete(*tree.get_children())
    for row in explanation["tile_rows"]:
        tree.insert("", tk.END, values=[str(row.get(col, "")) for col in _TILE_COLS])
    app.heuristics_note_var.set(explanation.get("admissibility_note", ""))


def reset_heuristics_tab(app: Any) -> None:
    """Return the Heuristics tab to its idle state (used on pre-search errors)."""
    app.heuristics_status_var.set(app._t("heuristics_idle"))
    for var in app.heuristics_totals.values():
        var.set("-")
    app.heuristics_tree.delete(*app.heuristics_tree.get_children())
    app.heuristics_note_var.set("")
