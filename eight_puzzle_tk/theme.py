"""Clean, modern ttk theme for the 8-Puzzle visualizer.

Applies a soft light palette with semantic widget styles (``Sidebar.*``,
``Card.*``, ``Primary.TButton``) and a polished Notebook tab look. Safe to call
once at app startup. All colors are listed in ``PALETTE`` for easy tweaking.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PALETTE = {
    "bg": "#f4f6fb",
    "sidebar_bg": "#e8eef9",
    "card_bg": "#ffffff",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_text": "#ffffff",
    "text": "#0f172a",
    "muted": "#64748b",
    "border": "#cbd5e1",
    "ok": "#16a34a",
    "warn": "#d97706",
    "err": "#dc2626",
    "cell_hover": "#dbeafe",
}


def apply_theme(root: tk.Tk) -> None:
    """Apply the visualizer theme. Call once before building widgets."""
    style = ttk.Style(root)
    themes = set(style.theme_names())
    for candidate in ("vista", "clam", "alt", "default"):
        if candidate in themes:
            style.theme_use(candidate)
            break

    root.configure(background=PALETTE["bg"])

    # Base ttk styles — keep platform defaults for unstyled widgets but set font.
    style.configure(".", font=("Segoe UI", 9))
    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])

    # Sidebar (left column with controls).
    style.configure("Sidebar.TFrame", background=PALETTE["sidebar_bg"])
    style.configure("Sidebar.TLabel", background=PALETTE["sidebar_bg"],
                    foreground=PALETTE["text"], font=("Segoe UI", 9))
    style.configure("SidebarHeading.TLabel", background=PALETTE["sidebar_bg"],
                    font=("Segoe UI", 10, "bold"), foreground=PALETTE["primary"])
    style.configure("Sidebar.TButton", font=("Segoe UI", 9))

    # Card (right column with tabs).
    style.configure("Card.TFrame", background=PALETTE["card_bg"])
    style.configure("Card.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["text"], font=("Segoe UI", 9))
    style.configure("CardHeading.TLabel", background=PALETTE["card_bg"],
                    font=("Segoe UI", 12, "bold"), foreground=PALETTE["primary"])
    style.configure("CardSubheading.TLabel", background=PALETTE["card_bg"],
                    font=("Segoe UI", 10, "bold"), foreground=PALETTE["text"])
    style.configure("PageTitle.TLabel", background=PALETTE["bg"],
                    font=("Segoe UI", 22, "bold"), foreground=PALETTE["text"])
    style.configure("Muted.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["muted"], font=("Segoe UI", 9))
    style.configure("Ok.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["ok"], font=("Segoe UI", 9, "bold"))
    style.configure("Err.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["err"], font=("Segoe UI", 9, "bold"))

    # LabelFrame (cards with a colored title bar).
    style.configure("TLabelFrame", background=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"])
    style.configure("TLabelFrame.Label", background=PALETTE["card_bg"],
                    foreground=PALETTE["primary"], font=("Segoe UI", 10, "bold"))

    # Notebook tabs.
    style.configure("TNotebook", background=PALETTE["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 9, "bold"))
    style.map(
        "TNotebook.Tab",
        background=[("selected", PALETTE["primary"]), ("active", PALETTE["cell_hover"])],
        foreground=[("selected", PALETTE["primary_text"])],
    )

    # Buttons.
    style.configure("TButton", font=("Segoe UI", 9), padding=(10, 5))
    style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"),
                    padding=(14, 6), foreground=PALETTE["primary_text"],
                    background=PALETTE["primary"])
    style.map("Primary.TButton", background=[("active", PALETTE["primary_hover"])])
    style.configure("Run.TButton", font=("Segoe UI", 10, "bold"),
                    padding=(16, 8), foreground=PALETTE["primary_text"],
                    background=PALETTE["primary"])
    style.map("Run.TButton", background=[("active", PALETTE["primary_hover"])])
    # Danger (red) — used for the main "Shuffle" CTA to match the reference.
    style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"),
                    padding=(14, 8), foreground="#ffffff",
                    background="#dc2626")
    style.map("Danger.TButton", background=[("active", "#b91c1c")])

    # Inputs.
    style.configure("TEntry", padding=4, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    style.configure("TSpinbox", padding=4, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    style.configure("TCombobox", padding=4, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    # Matrix cell entry (compact, square-ish, white with subtle border).
    style.configure("Matrix.TEntry", padding=2, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])

    # Treeview.
    style.configure("Treeview", rowheight=26, font=("Segoe UI", 9),
                    background=PALETTE["card_bg"], fieldbackground=PALETTE["card_bg"],
                    foreground=PALETTE["text"])
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                    background=PALETTE["sidebar_bg"], foreground=PALETTE["text"])
    style.map("Treeview.Heading", background=[("active", PALETTE["cell_hover"])])
    style.map("Treeview", background=[("selected", PALETTE["cell_hover"])])

    # Scrollbar.
    style.configure("Vertical.TScrollbar", background=PALETTE["sidebar_bg"],
                    bordercolor=PALETTE["border"], arrowcolor=PALETTE["muted"])
