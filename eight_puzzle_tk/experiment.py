"""Bounded coursework experiment: run all default algorithms on demo presets.

The Experiment tab is a one-click coursework benchmark. It calls
:func:`run_experiment_suite` from the core module, then renders the result
rows + baseline costs in a Treeview. The tab is independent of the sidebar's
current start/goal state — it always uses the demo presets so results are
comparable across runs.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

from eight_puzzle_search_app import run_experiment_suite


_EXP_COLS: tuple = (
    "Preset", "Algorithm", "Found", "Path Cost", "Expanded", "Generated",
    "Runtime ms", "Memory", "Complete", "Optimal", "Optimal Gap", "Message",
)
_WIDTHS = {
    "Preset": 110, "Algorithm": 110, "Found": 60, "Path Cost": 80,
    "Expanded": 80, "Generated": 80, "Runtime ms": 90, "Memory": 110,
    "Complete": 110, "Optimal": 90, "Optimal Gap": 100, "Message": 220,
}


def build_experiment_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Experiment tab widgets and store refs on ``app``."""
    app._i18n_labels["experiment_title"] = ttk.Label(
        parent, text=app._t("experiment_title"), font=("", 12, "bold"),
    )
    app._i18n_labels["experiment_title"].pack(anchor=tk.W, pady=(0, 6))

    bar = ttk.Frame(parent)
    bar.pack(fill=tk.X, pady=(0, 6))
    app._i18n_labels["experiment_run"] = ttk.Button(
        bar, text=app._t("experiment_run"), command=app._on_experiment_run,
    )
    app._i18n_labels["experiment_run"].pack(side=tk.LEFT)

    app.experiment_status_var = tk.StringVar(value=app._t("experiment_idle"))
    ttk.Label(parent, textvariable=app.experiment_status_var).pack(anchor=tk.W)

    baseline_frame = ttk.LabelFrame(
        parent, text=app._t("experiment_baseline"), padding=8,
    )
    baseline_frame.pack(fill=tk.X, pady=(8, 0))
    app.experiment_baseline_var = tk.StringVar(value="-")
    ttk.Label(
        baseline_frame, textvariable=app.experiment_baseline_var,
        wraplength=640, justify=tk.LEFT,
    ).pack(anchor=tk.W)

    table_frame = ttk.LabelFrame(
        parent, text=app._t("experiment_table"), padding=8,
    )
    table_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    tree = ttk.Treeview(
        table_frame, columns=_EXP_COLS, show="headings", height=12,
    )
    for col in _EXP_COLS:
        tree.heading(col, text=col)
        tree.column(col, width=_WIDTHS.get(col, 80), anchor=tk.W)
    tree.tag_configure("found", foreground="#0a0")
    tree.tag_configure("missed", foreground="#a00")
    tree.tag_configure("optimal_gap", foreground="#a60")
    app.experiment_tree = tree
    tree.pack(fill=tk.BOTH, expand=True)


def populate_experiment_tab(app: Any, result: Dict[str, Any]) -> None:
    """Refresh the Experiment tab from a run_experiment_suite() result dict."""
    tree = app.experiment_tree
    tree.delete(*tree.get_children())
    rows = result.get("rows", [])
    for row in rows:
        values = [str(row.get(col, "")) for col in _EXP_COLS]
        tags = []
        if not row.get("Found", True):
            tags.append("missed")
        gap = row.get("Optimal Gap", "")
        if isinstance(gap, int) and gap > 0:
            tags.append("optimal_gap")
        elif row.get("Found", True):
            tags.append("found")
        tree.insert("", tk.END, values=values, tags=tuple(tags) or ("found",))

    baselines = result.get("baselines", {}) or {}
    if baselines:
        parts = [
            f"{preset} = {cost if cost is not None else app._t('experiment_no_baseline')}"
            for preset, cost in baselines.items()
        ]
        app.experiment_baseline_var.set("  |  ".join(parts))
    else:
        app.experiment_baseline_var.set("-")

    app.experiment_status_var.set(
        app._t("experiment_done").format(
            rows=len(rows), presets=len(result.get("presets", [])),
            algorithms=len(result.get("algorithms", [])),
        )
    )
    app.experiment_last_result = result


def reset_experiment_tab(app: Any) -> None:
    """Clear the Experiment tab to its idle state."""
    app.experiment_tree.delete(*app.experiment_tree.get_children())
    app.experiment_status_var.set(app._t("experiment_idle"))
    app.experiment_baseline_var.set("-")
    app.experiment_last_result = None
