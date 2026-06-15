"""Side-by-side comparison of multiple algorithms on the same start/goal state.

The Compare tab has its own group combobox (defaults to the sidebar's group)
plus a Run button. The sidebar's "Compare all" button is a shortcut that runs
the current group and switches to this tab. Result table is filled from
:py:meth:`SearchResult.summary_row`.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, List

from eight_puzzle_search_app import SearchResult


_COMPARE_COLS: tuple = (
    "Algorithm", "Group", "Found", "Path Length", "Expanded", "Generated",
    "Max Frontier", "Reached", "Runtime ms", "Optimal", "Complete", "Memory", "Message",
)
_WIDTHS = {
    "Algorithm": 110, "Group": 130, "Found": 60, "Path Length": 90,
    "Expanded": 80, "Generated": 80, "Max Frontier": 100, "Reached": 70,
    "Runtime ms": 90, "Optimal": 90, "Complete": 110, "Memory": 110, "Message": 220,
}


def build_compare_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Compare tab widgets and store refs on ``app``."""
    app._i18n_labels["compare_title"] = ttk.Label(
        parent, text=app._t("compare_title"), font=("", 12, "bold"),
    )
    app._i18n_labels["compare_title"].pack(anchor=tk.W, pady=(0, 6))

    bar = ttk.Frame(parent)
    bar.pack(fill=tk.X, pady=(0, 6))
    app._i18n_labels["compare_group"] = ttk.Label(bar, text=app._t("compare_group"))
    app._i18n_labels["compare_group"].pack(side=tk.LEFT)
    initial_group = app.group_var.get() if hasattr(app, "group_var") else ""
    groups = app.algorithm_groups_list if hasattr(app, "algorithm_groups_list") else []
    app.compare_group_var = tk.StringVar(value=initial_group)
    ttk.Combobox(
        bar, textvariable=app.compare_group_var, values=groups,
        state="readonly", width=24,
    ).pack(side=tk.LEFT, padx=4)
    app._i18n_labels["compare_run"] = ttk.Button(
        bar, text=app._t("compare_run"), command=app._on_compare_run,
    )
    app._i18n_labels["compare_run"].pack(side=tk.LEFT, padx=4)

    app.compare_status_var = tk.StringVar(value=app._t("compare_idle"))
    ttk.Label(parent, textvariable=app.compare_status_var).pack(anchor=tk.W)

    table_frame = ttk.LabelFrame(parent, text=app._t("compare_table"), padding=8)
    table_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    tree = ttk.Treeview(
        table_frame, columns=_COMPARE_COLS, show="headings", height=10,
    )
    for col in _COMPARE_COLS:
        tree.heading(col, text=col)
        tree.column(col, width=_WIDTHS.get(col, 80), anchor=tk.W)
    tree.tag_configure("found", foreground="#0a0")
    tree.tag_configure("missed", foreground="#a00")
    app.compare_tree = tree
    tree.pack(fill=tk.BOTH, expand=True)


def populate_compare_tab(app: Any, results: List[SearchResult], group: str) -> None:
    """Refresh the Compare tab from a list of SearchResults."""
    tree = app.compare_tree
    tree.delete(*tree.get_children())
    for r in results:
        row = {"Group": group}
        row.update(r.summary_row())
        values = [str(row.get(col, "")) for col in _COMPARE_COLS]
        tag = "found" if r.found else "missed"
        tree.insert("", tk.END, values=values, tags=(tag,))
    app.compare_status_var.set(
        app._t("compare_done").format(count=len(results), group=group)
    )


def reset_compare_tab(app: Any) -> None:
    """Clear the Compare tab to its idle state."""
    app.compare_tree.delete(*app.compare_tree.get_children())
    app.compare_status_var.set(app._t("compare_idle"))
