"""Render SearchResult and its academic certificate into the Summary tab.

The Summary tab is a small read-only dashboard: status line, metrics table,
and a green/red certificate block. The Run button in the App calls
:meth:`eight_puzzle_search_app.run_algorithm`, then :func:`populate_summary`
to refresh the widgets in place.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List

from eight_puzzle_search_app import SearchResult, academic_conclusion


_METRIC_KEYS: List[str] = [
    "algorithm", "heuristic", "path_cost", "expanded", "generated",
    "max_frontier", "reached", "runtime_ms", "memory_kb", "optimal", "complete",
]

_CERT_KEYS: List[str] = [
    "path_valid", "cost_matches_actions", "terminal_matches_goal",
    "solvability_checked", "heuristic_values_valid",
]


def _make_kv_row(parent: tk.Misc, app: Any, label_key: str) -> tk.StringVar:
    row = ttk.Frame(parent)
    row.pack(fill=tk.X, pady=1)
    app._i18n_labels[label_key] = ttk.Label(
        row, text=app._t(label_key), width=22, anchor=tk.W,
    )
    app._i18n_labels[label_key].pack(side=tk.LEFT)
    var = tk.StringVar(value="-")
    ttk.Label(row, textvariable=var, anchor=tk.W).pack(side=tk.LEFT, padx=(8, 0))
    return var


def build_summary_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Summary tab widgets and store their StringVars on ``app``."""
    app._i18n_labels["summary_title"] = ttk.Label(
        parent, text=app._t("summary_title"), font=("", 12, "bold"),
    )
    app._i18n_labels["summary_title"].pack(anchor=tk.W, pady=(0, 6))

    app.summary_status_var = tk.StringVar(value=app._t("summary_idle"))
    ttk.Label(parent, textvariable=app.summary_status_var).pack(anchor=tk.W)

    metrics_frame = ttk.LabelFrame(parent, text=app._t("summary_metrics"), padding=8)
    metrics_frame.pack(fill=tk.X, pady=(8, 0))
    app.summary_metrics = {
        key: _make_kv_row(metrics_frame, app, f"summary_{key}") for key in _METRIC_KEYS
    }

    cert_frame = ttk.LabelFrame(parent, text=app._t("summary_certificate"), padding=8)
    cert_frame.pack(fill=tk.X, pady=(8, 0))
    app.summary_certificate = {
        key: _make_kv_row(cert_frame, app, f"cert_{key}") for key in _CERT_KEYS
    }

    app._i18n_labels["summary_error_label"] = ttk.Label(parent, text=app._t("summary_error"))
    app._i18n_labels["summary_error_label"].pack(anchor=tk.W, pady=(8, 0))
    app.summary_error_var = tk.StringVar(value="")
    ttk.Label(
        parent, textvariable=app.summary_error_var, foreground="#a00", wraplength=640,
    ).pack(anchor=tk.W)

    app.summary_conclusion_var = tk.StringVar(value="")
    ttk.Label(
        parent, textvariable=app.summary_conclusion_var, wraplength=640, justify=tk.LEFT,
    ).pack(anchor=tk.W, pady=(8, 0))


def populate_summary(app: Any, result: SearchResult, certificate: Dict[str, Any]) -> None:
    """Update the Summary tab widgets from a SearchResult + its certificate."""
    unsolvable = (
        not certificate.get("solvability_checked", True)
        or "Unsolvable" in result.message
    )
    if unsolvable:
        status = app._t("summary_unsolvable")
    elif result.found:
        status = app._t("summary_found")
    else:
        status = app._t("summary_not_found")
    app.summary_status_var.set(status)

    m = app.summary_metrics
    m["algorithm"].set(result.algorithm)
    m["heuristic"].set(getattr(app, "heuristic_var", tk.StringVar(value="")).get() or "-")
    m["path_cost"].set(str(result.path_cost) if result.path_cost is not None else "-")
    m["expanded"].set(str(result.expanded))
    m["generated"].set(str(result.generated))
    m["max_frontier"].set(str(result.max_frontier))
    m["reached"].set(str(result.reached_count))
    m["runtime_ms"].set(f"{result.runtime_ms:.3f}")
    m["memory_kb"].set(f"{result.memory_estimate_kb:.1f}")
    m["optimal"].set(result.optimal)
    m["complete"].set(result.complete)

    pass_label = app._t("cert_pass")
    fail_label = app._t("cert_fail")
    for key, var in app.summary_certificate.items():
        passed = bool(certificate.get(key, False))
        var.set((pass_label if passed else fail_label))

    app.summary_error_var.set(certificate.get("error", "") or "")
    app.summary_conclusion_var.set(academic_conclusion(result))


def show_error_state(app: Any, message: str) -> None:
    """Reset the Summary tab to a visible error state without running search."""
    app.summary_status_var.set(app._t("summary_idle"))
    for var in app.summary_metrics.values():
        var.set("-")
    for var in app.summary_certificate.values():
        var.set("-")
    app.summary_error_var.set(message)
    app.summary_conclusion_var.set("")
