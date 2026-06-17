"""Academic content card: PEAS problem model + selected algorithm profile.

Rendered inside the right-hand card of the main area. Each section is
collapsible: clicking the header toggles the content visibility and the
arrow indicator.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Tuple


def _add_expandable_section(
    parent: tk.Misc,
    app: Any,
    title_key: str,
    items: List[Tuple[str, str]],
    *,
    expanded: bool = True,
) -> None:
    """Build a collapsible section with a title and (label, text) rows.

    ``items`` is a list of ``(label_i18n_key, text_i18n_key)`` pairs. The label
    is rendered bold inline with the text, matching the reference layout.
    """
    header = ttk.Frame(parent, style="Card.TFrame", cursor="hand2")
    header.pack(fill=tk.X, pady=(12, 0), anchor=tk.W)

    arrow_var = tk.StringVar(value="v" if expanded else ">")
    arrow = ttk.Label(
        header, textvariable=arrow_var,
        style="CardSubheading.TLabel", width=2,
    )
    arrow.pack(side=tk.LEFT)
    title_lbl = ttk.Label(header, text=app._t(title_key), style="CardSubheading.TLabel")
    title_lbl.pack(side=tk.LEFT, padx=(4, 0))

    body = ttk.Frame(parent, style="Card.TFrame")
    if expanded:
        body.pack(fill=tk.X, padx=(20, 0), pady=(4, 0))

    for label_key, text_key in items:
        row = ttk.Frame(body, style="Card.TFrame")
        row.pack(fill=tk.X, pady=3, anchor=tk.W)
        bold = ttk.Label(
            row, text=app._t(label_key),
            style="Card.TLabel", font=("Segoe UI", 9, "bold"),
        )
        bold.pack(side=tk.LEFT, anchor=tk.NW)
        text = ttk.Label(
            row, text=app._t(text_key),
            style="Card.TLabel", wraplength=420, justify=tk.LEFT,
        )
        text.pack(side=tk.LEFT, anchor=tk.NW, padx=(4, 0))

    def toggle(_event: Optional[tk.Event] = None) -> None:
        if body.winfo_ismapped():
            body.pack_forget()
            arrow_var.set(">")
        else:
            body.pack(fill=tk.X, padx=(20, 0), pady=(4, 0))
            arrow_var.set("v")

    for w in (header, arrow, title_lbl):
        w.bind("<Button-1>", toggle, add="+")


def build_academic_card(parent: tk.Misc, app: Any) -> None:
    """Build the PEAS + algorithm profile content into ``parent``."""
    _add_expandable_section(
        parent, app, "academic_peas_title",
        [
            ("academic_peas_performance_label", "academic_peas_performance_text"),
            ("academic_peas_environment_label", "academic_peas_environment_text"),
            ("academic_peas_actuators_label", "academic_peas_actuators_text"),
            ("academic_peas_sensors_label", "academic_peas_sensors_text"),
        ],
    )
    _add_expandable_section(
        parent, app, "academic_algo_profile_title",
        [("academic_algo_coming_soon", "academic_algo_coming_soon")],
        expanded=False,
    )
