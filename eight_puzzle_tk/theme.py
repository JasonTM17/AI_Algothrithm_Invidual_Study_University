"""Modern flat ttk theme for the 8-Puzzle visualizer.

Matches the Streamlit web app's clean card-based UI as closely as Tkinter allows.
Forces the "clam" theme so custom colors/borders actually render on Windows.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PALETTE = {
    "bg": "#f8fafc",
    "sidebar_bg": "#f1f5f9",
    "card_bg": "#ffffff",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_text": "#ffffff",
    "text": "#0f172a",
    "muted": "#64748b",
    "border": "#e2e8f0",
    "ok": "#16a34a",
    "ok_soft": "#dcfce7",
    "ok_text": "#166534",
    "warn": "#d97706",
    "err": "#dc2626",
    "err_soft": "#fee2e2",
    "err_text": "#991b1b",
    "cell_hover": "#dbeafe",
    "danger": "#dc2626",
    "danger_hover": "#b91c1c",
    "blank_tile_bg": "#eff6ff",
    "blank_tile_fg": "#2563eb",
    "tile_bg": "#ffffff",
    "tile_border": "#334155",
    "invalid_bg": "#fee2e2",
}


def apply_theme(root: tk.Tk) -> None:
    """Apply the visualizer theme. Call once before building widgets."""
    style = ttk.Style(root)
    themes = set(style.theme_names())
    # clam is required for custom fieldbackground/bordercolor to work reliably.
    for candidate in ("clam", "alt", "default", "vista"):
        if candidate in themes:
            style.theme_use(candidate)
            break

    root.configure(background=PALETTE["bg"])

    # Base
    style.configure(".", font=("Segoe UI", 10))
    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])

    # Sidebar
    style.configure("Sidebar.TFrame", background=PALETTE["sidebar_bg"])
    style.configure("Sidebar.TLabel", background=PALETTE["sidebar_bg"],
                    foreground=PALETTE["text"], font=("Segoe UI", 10))
    style.configure("SidebarHeading.TLabel", background=PALETTE["sidebar_bg"],
                    font=("Segoe UI", 10, "bold"), foreground=PALETTE["primary"])
    style.configure("Sidebar.TButton", font=("Segoe UI", 10))
    style.configure("SidebarGroup.TLabelframe", background=PALETTE["sidebar_bg"],
                    bordercolor=PALETTE["border"])
    style.configure("SidebarGroup.TLabelframe.Label",
                    background=PALETTE["sidebar_bg"], foreground=PALETTE["muted"],
                    font=("Segoe UI", 9, "bold"))

    # Card
    style.configure("Card.TFrame", background=PALETTE["card_bg"])
    style.configure("Card.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["text"], font=("Segoe UI", 10))
    style.configure("CardHeading.TLabel", background=PALETTE["card_bg"],
                    font=("Segoe UI", 14, "bold"), foreground=PALETTE["text"])
    style.configure("CardSubheading.TLabel", background=PALETTE["card_bg"],
                    font=("Segoe UI", 11, "bold"), foreground=PALETTE["text"])
    style.configure("PageTitle.TLabel", background=PALETTE["bg"],
                    font=("Segoe UI", 24, "bold"), foreground=PALETTE["text"])
    style.configure("PageSubtitle.TLabel", background=PALETTE["bg"],
                    font=("Segoe UI", 10, "bold"), foreground=PALETTE["primary"])
    style.configure("Muted.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["muted"], font=("Segoe UI", 10))
    style.configure("Ok.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["ok"], font=("Segoe UI", 10, "bold"))
    style.configure("Err.TLabel", background=PALETTE["card_bg"],
                    foreground=PALETTE["err"], font=("Segoe UI", 10, "bold"))

    # LabelFrame
    style.configure("TLabelFrame", background=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"])
    style.configure("TLabelFrame.Label", background=PALETTE["card_bg"],
                    foreground=PALETTE["primary"], font=("Segoe UI", 10, "bold"))

    # Notebook tabs — underline-style active tab.
    style.configure("TNotebook", background=PALETTE["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 10), font=("Segoe UI", 10, "bold"))
    style.map(
        "TNotebook.Tab",
        background=[("selected", PALETTE["bg"]), ("active", PALETTE["bg"])],
        foreground=[("selected", PALETTE["primary"]), ("active", PALETTE["primary"])],
        expand=[("selected", [0, 0, 2, 0])],
    )

    # Buttons
    style.configure("TButton", font=("Segoe UI", 10), padding=(10, 5))
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"),
                    padding=(14, 6), foreground=PALETTE["primary_text"],
                    background=PALETTE["primary"])
    style.map("Primary.TButton", background=[("active", PALETTE["primary_hover"])])
    style.configure("Run.TButton", font=("Segoe UI", 11, "bold"),
                    padding=(16, 8), foreground=PALETTE["primary_text"],
                    background=PALETTE["primary"])
    style.map("Run.TButton", background=[("active", PALETTE["primary_hover"])])
    style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"),
                    padding=(14, 8), foreground=PALETTE["primary_text"],
                    background=PALETTE["danger"])
    style.map("Danger.TButton", background=[("active", PALETTE["danger_hover"])])

    # Inputs
    style.configure("TEntry", padding=5, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    style.configure("TSpinbox", padding=5, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    style.configure("TCombobox", padding=5, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    style.configure("Matrix.TEntry", padding=2, fieldbackground=PALETTE["card_bg"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])

    # Treeview
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10),
                    background=PALETTE["card_bg"], fieldbackground=PALETTE["card_bg"],
                    foreground=PALETTE["text"])
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    background=PALETTE["sidebar_bg"], foreground=PALETTE["text"])
    style.map("Treeview.Heading", background=[("active", PALETTE["cell_hover"])])
    style.map("Treeview", background=[("selected", PALETTE["cell_hover"])])

    # Scrollbar
    style.configure("Vertical.TScrollbar", background=PALETTE["sidebar_bg"],
                    bordercolor=PALETTE["border"], arrowcolor=PALETTE["muted"])
