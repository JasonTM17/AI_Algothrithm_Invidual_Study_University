"""Render SearchResult.trace_rows into a scrollable Tkinter Treeview.

The trace is a read-only step log: one row per expansion, columns from
``eight_puzzle_search_app.TRACE_COLUMNS``. Column headings are kept in English
because they match the technical vocabulary in the core module; titles and
status messages are translated via the app's bilingual i18n.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from eight_puzzle_search_app import TRACE_COLUMNS, SearchResult


# Tuned for the 8-puzzle state strings emitted by the core module.
_COL_WIDTHS: dict = {
    "Step": 50, "Algorithm": 90, "Node": 60, "Action": 70, "Depth": 50,
    "g": 40, "h": 40, "f": 40,
    "Priority Rule": 100, "Selection Key": 100,
    "Generated Children": 160, "Skipped States": 130,
    "Frontier": 160, "Reached": 140, "Decision/Note": 200,
}
_RIGHT_ALIGNED = {"Step", "Depth", "g", "h", "f"}


def build_trace_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Trace tab widgets and store the Treeview on ``app``."""
    app._i18n_labels["trace_title"] = ttk.Label(
        parent, text=app._t("trace_title"), font=("", 12, "bold"),
    )
    app._i18n_labels["trace_title"].pack(anchor=tk.W, pady=(0, 6))

    app.trace_status_var = tk.StringVar(value=app._t("trace_idle"))
    ttk.Label(parent, textvariable=app.trace_status_var).pack(anchor=tk.W)

    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    tree = ttk.Treeview(
        tree_frame, columns=TRACE_COLUMNS, show="headings", height=20,
    )
    for col in TRACE_COLUMNS:
        tree.heading(col, text=col)
        tree.column(
            col,
            width=_COL_WIDTHS.get(col, 80),
            anchor=tk.E if col in _RIGHT_ALIGNED else tk.W,
            stretch=False,
        )
    app.trace_tree = tree

    vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)


def populate_trace_tab(app: Any, result: SearchResult) -> None:
    """Refresh the Trace Treeview from ``result.trace_rows``."""
    tree = app.trace_tree
    tree.delete(*tree.get_children())
    if not result.trace_rows:
        app.trace_status_var.set(app._t("trace_empty"))
        return
    for row in result.trace_rows:
        values = [str(row.get(col, "")) for col in TRACE_COLUMNS]
        tree.insert("", tk.END, values=values)
    app.trace_status_var.set(f"{len(result.trace_rows)} rows")


def reset_trace_tab(app: Any) -> None:
    """Return the Trace tab to its idle state (used on pre-search errors)."""
    app.trace_tree.delete(*app.trace_tree.get_children())
    app.trace_status_var.set(app._t("trace_idle"))
