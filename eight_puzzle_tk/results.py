"""Render SearchResult and its academic certificate into the Summary tab.

The Summary tab is a small read-only dashboard: status line, metric cards grid,
and a green/red certificate block. The Run button in the App calls
:meth:`eight_puzzle_search_app.run_algorithm`, then :func:`populate_summary`
to refresh the widgets in place.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List

from eight_puzzle_search_app import SearchResult, academic_conclusion
from .theme import PALETTE


_METRIC_KEYS: List[str] = [
    "algorithm", "heuristic", "path_cost", "expanded", "generated",
    "max_frontier", "reached", "runtime_ms", "memory_kb", "optimal", "complete",
]

_CERT_KEYS: List[str] = [
    "path_valid", "cost_matches_actions", "terminal_matches_goal",
    "solvability_checked", "heuristic_values_valid",
]


def _make_metric_card(parent: tk.Misc, app: Any, label_key: str):
    """Build a single metric card: small frame with label + value."""
    card = tk.Frame(
        parent, bg=PALETTE["card_bg"], highlightbackground=PALETTE["border"],
        highlightthickness=1, padx=10, pady=8,
    )
    app._i18n_labels[label_key] = ttk.Label(
        card, text=app._t(label_key), font=("Segoe UI", 10),
        foreground=PALETTE["muted"], background=PALETTE["card_bg"],
    )
    app._i18n_labels[label_key].pack(anchor=tk.W)
    var = tk.StringVar(value="-")
    tk.Label(
        card, textvariable=var, font=("Segoe UI", 14, "bold"),
        foreground=PALETTE["text"], bg=PALETTE["card_bg"], anchor=tk.W,
    ).pack(anchor=tk.W, pady=(2, 0))
    return var, card


def _make_chip_row(parent: tk.Misc, app: Any, label_key: str) -> tk.Label:
    """Build a cert row with a colored pass/fail chip."""
    row = tk.Frame(parent, bg=PALETTE["card_bg"])
    row.pack(fill=tk.X, pady=3)
    app._i18n_labels[label_key] = tk.Label(
        row, text=app._t(label_key), width=32, anchor=tk.W,
        bg=PALETTE["card_bg"], fg=PALETTE["text"],
        font=("Segoe UI", 10),
    )
    app._i18n_labels[label_key].pack(side=tk.LEFT)
    chip = tk.Label(
        row, text="-", font=("Segoe UI", 9, "bold"),
        padx=10, pady=2, relief=tk.FLAT, borderwidth=0,
        bg=PALETTE["sidebar_bg"], fg=PALETTE["muted"],
    )
    chip.pack(side=tk.LEFT, padx=(8, 0))
    return chip


def build_summary_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Summary tab widgets and store their StringVars on ``app``."""
    app._i18n_labels["summary_title"] = ttk.Label(
        parent, text=app._t("summary_title"),
        style="CardHeading.TLabel",
    )
    app._i18n_labels["summary_title"].pack(anchor=tk.W, pady=(0, 4))

    app.summary_status_var = tk.StringVar(value=app._t("summary_idle"))
    tk.Label(
        parent, textvariable=app.summary_status_var,
        font=("Segoe UI", 10), bg=PALETTE["card_bg"], fg=PALETTE["muted"],
    ).pack(anchor=tk.W)

    # Metric cards in a wrapping grid
    metrics_frame = ttk.LabelFrame(
        parent, text=app._t("summary_metrics"), padding=12,
    )
    metrics_frame.pack(fill=tk.X, pady=(10, 0))
    app.summary_metrics: Dict[str, tk.StringVar] = {}
    app._metric_cards: List[tk.Frame] = []
    cols = 4
    for idx, key in enumerate(_METRIC_KEYS):
        var, card = _make_metric_card(metrics_frame, app, f"summary_{key}")
        app.summary_metrics[key] = var
        app._metric_cards.append(card)
        row = idx // cols
        col = idx % cols
        card.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")
    for c in range(cols):
        metrics_frame.columnconfigure(c, weight=1)

    # Certificate section with colored chips
    cert_frame = ttk.LabelFrame(
        parent, text=app._t("summary_certificate"), padding=12,
    )
    cert_frame.pack(fill=tk.X, pady=(10, 0))
    app._cert_chips: Dict[str, tk.Label] = {}
    for key in _CERT_KEYS:
        app._cert_chips[key] = _make_chip_row(cert_frame, app, f"cert_{key}")

    app._i18n_labels["summary_error_label"] = ttk.Label(
        parent, text=app._t("summary_error"),
    )
    app._i18n_labels["summary_error_label"].pack(anchor=tk.W, pady=(10, 0))
    app.summary_error_var = tk.StringVar(value="")
    ttk.Label(
        parent, textvariable=app.summary_error_var, foreground=PALETTE["err"],
        wraplength=700, justify=tk.LEFT,
    ).pack(anchor=tk.W)

    app.summary_conclusion_var = tk.StringVar(value="")
    ttk.Label(
        parent, textvariable=app.summary_conclusion_var,
        wraplength=700, justify=tk.LEFT,
    ).pack(anchor=tk.W, pady=(10, 0))


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
    for key, chip in app._cert_chips.items():
        passed = bool(certificate.get(key, False))
        chip.config(
            text=(pass_label if passed else fail_label),
            bg=PALETTE["ok_soft"] if passed else PALETTE["err_soft"],
            fg=PALETTE["ok_text"] if passed else PALETTE["err_text"],
        )


def show_error_state(app: Any, message: str) -> None:
    """Reset the Summary tab to a visible error state without running search."""
    app.summary_status_var.set(app._t("summary_idle"))
    for var in app.summary_metrics.values():
        var.set("-")
    for key, chip in app._cert_chips.items():
        chip.config(text="-", bg=PALETTE["sidebar_bg"], fg=PALETTE["muted"])
    app.summary_error_var.set(message)
    app.summary_conclusion_var.set("")
