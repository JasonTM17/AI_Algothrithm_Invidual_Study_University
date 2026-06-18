"""Academic content card: PEAS, problem definition, evaluation criteria,
trace glossary, and selected algorithm profile.

Rendered inside the right-hand card of the main area. Each section is
collapsible: clicking the header toggles the content visibility and the
arrow indicator.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Tuple

from .theme import PALETTE


def _add_expandable_section(
    parent: tk.Misc,
    app: Any,
    title_key: str,
    items: List[Tuple[str, str]],
    *,
    expanded: bool = True,
) -> None:
    """Build a collapsible section with a title and (label, text) rows."""
    header = tk.Frame(parent, bg=PALETTE["card_bg"], cursor="hand2")
    header.pack(fill=tk.X, pady=(10, 0), anchor=tk.W)

    arrow_var = tk.StringVar(value="v" if expanded else ">")
    arrow = tk.Label(
        header, textvariable=arrow_var,
        font=("Segoe UI", 10, "bold"),
        bg=PALETTE["card_bg"], fg=PALETTE["primary"], width=2, anchor=tk.W,
    )
    arrow.pack(side=tk.LEFT)
    title_lbl = tk.Label(
        header, text=app._t(title_key),
        font=("Segoe UI", 11, "bold"),
        bg=PALETTE["card_bg"], fg=PALETTE["text"],
    )
    title_lbl.pack(side=tk.LEFT, padx=(4, 0))

    body = tk.Frame(parent, bg=PALETTE["card_bg"])
    if expanded:
        body.pack(fill=tk.X, pady=(4, 0))

    for label_key, text_key in items:
        row = tk.Frame(body, bg=PALETTE["card_bg"])
        row.pack(fill=tk.X, pady=(6, 2), anchor=tk.W)
        # Stack label on top, text below — much more readable in a narrow column.
        bold = tk.Label(
            row, text=app._t(label_key),
            font=("Segoe UI", 10, "bold"),
            bg=PALETTE["card_bg"], fg=PALETTE["text"],
            anchor=tk.W, justify=tk.LEFT,
        )
        bold.pack(fill=tk.X, anchor=tk.W)
        text = tk.Label(
            row, text=app._t(text_key),
            font=("Segoe UI", 10),
            bg=PALETTE["card_bg"], fg=PALETTE["muted"],
            wraplength=560, anchor=tk.W, justify=tk.LEFT,
        )
        text.pack(fill=tk.X, anchor=tk.W, pady=(1, 0))

    def toggle(_event: Optional[tk.Event] = None) -> None:
        if body.winfo_ismapped():
            body.pack_forget()
            arrow_var.set(">")
        else:
            body.pack(fill=tk.X, pady=(4, 0))
            arrow_var.set("v")

    for w in (header, arrow, title_lbl):
        w.bind("<Button-1>", toggle, add="+")


def build_academic_card(parent: tk.Misc, app: Any) -> None:
    """Build all academic sections into ``parent``."""
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
        parent, app, "academic_problem_def_title",
        [
            ("academic_pd_objective_label", "academic_pd_objective_text"),
            ("academic_pd_state_space_label", "academic_pd_state_space_text"),
            ("academic_pd_transition_label", "academic_pd_transition_text"),
            ("academic_pd_heuristic_label", "academic_pd_heuristic_text"),
        ],
    )
    _add_expandable_section(
        parent, app, "academic_evaluation_title",
        [
            ("academic_eval_complete_label", "academic_eval_complete_text"),
            ("academic_eval_optimal_label", "academic_eval_optimal_text"),
            ("academic_eval_expanded_label", "academic_eval_expanded_text"),
            ("academic_eval_frontier_label", "academic_eval_frontier_text"),
            ("academic_eval_runtime_label", "academic_eval_runtime_text"),
        ],
        expanded=False,
    )
    _add_expandable_section(
        parent, app, "academic_glossary_title",
        [
            ("academic_glossary_node_label", "academic_glossary_node_text"),
            ("academic_glossary_frontier_label", "academic_glossary_frontier_text"),
            ("academic_glossary_reached_label", "academic_glossary_reached_text"),
            ("academic_glossary_priority_label", "academic_glossary_priority_text"),
            ("academic_glossary_key_label", "academic_glossary_key_text"),
        ],
        expanded=False,
    )
    _add_expandable_section(
        parent, app, "academic_algo_profile_title",
        [("academic_algo_coming_soon", "academic_algo_coming_soon")],
        expanded=False,
    )
