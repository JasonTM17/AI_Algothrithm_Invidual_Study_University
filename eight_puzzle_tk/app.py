"""Tkinter App class — minimal scaffold with sidebar, language toggle, placeholder.

Subsequent commits replace the placeholder with sidebar controls, matrix editors,
algorithm selectors, run/compare buttons, and the result tabs (Summary / Trace /
Heuristics / Experiment / Report).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from .i18n import DEFAULT_LANG, t


class App:
    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.lang: str = DEFAULT_LANG
        self.root = root or tk.Tk()
        self.root.title(t("app_title", self.lang))
        self.root.geometry("1280x820")
        self.root.minsize(1024, 720)
        self._build_layout()

    def _build_layout(self) -> None:
        self.sidebar = ttk.Frame(self.root, padding=8)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.main_area = ttk.Frame(self.root, padding=8)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_language_toggle()
        self._build_placeholder()

    def _build_language_toggle(self) -> None:
        bar = ttk.Frame(self.sidebar)
        bar.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(bar, text=t("language", self.lang)).pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.lang)
        ttk.Radiobutton(
            bar,
            text=t("lang_vi", self.lang),
            value="vi",
            variable=self.lang_var,
            command=self._on_lang_change,
        ).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(
            bar,
            text=t("lang_en", self.lang),
            value="en",
            variable=self.lang_var,
            command=self._on_lang_change,
        ).pack(side=tk.LEFT, padx=4)

    def _build_placeholder(self) -> None:
        ttk.Label(
            self.sidebar,
            text=t("section_controls", self.lang),
            font=("", 11, "bold"),
        ).pack(anchor=tk.W, pady=(8, 4))
        ttk.Label(
            self.main_area,
            text=t("coming_soon", self.lang),
        ).pack()

    def _on_lang_change(self) -> None:
        self.lang = self.lang_var.get()
        self.root.title(t("app_title", self.lang))

    def run(self) -> None:
        self.root.mainloop()


def run() -> None:
    App().run()


if __name__ == "__main__":
    run()
