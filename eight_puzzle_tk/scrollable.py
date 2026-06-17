"""Scrollable ttk.Frame wrapper with vertical scrollbar and mouse-wheel support.

Children must be packed/gridded into ``self.inner``. Mouse-wheel events are
dispatched to whichever ScrolledFrame the cursor is currently over, so multiple
ScrolledFrames in the same window cooperate cleanly.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional


class ScrolledFrame(ttk.Frame):
    """A ttk.Frame containing a Canvas + vertical Scrollbar + inner ttk.Frame."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        bg: Optional[str] = None,
        padding: int = 0,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)
        bg = bg or "white"
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, background=bg)
        self.vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.inner = ttk.Frame(self.canvas, padding=padding)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        for w in (self.canvas, self.inner):
            w.bind("<Enter>", self._on_enter, add="+")
            w.bind("<Leave>", self._on_leave, add="+")

    def _on_inner_configure(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self._win_id, width=event.width)

    def _on_enter(self, _event: tk.Event) -> None:
        self.canvas.bind_all("<MouseWheel>", self._dispatch_wheel)
        self.canvas.bind_all("<Button-4>", self._dispatch_wheel_up)
        self.canvas.bind_all("<Button-5>", self._dispatch_wheel_down)

    def _on_leave(self, _event: tk.Event) -> None:
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    @staticmethod
    def _scrolled_frame_under(widget: tk.Misc) -> Optional["ScrolledFrame"]:
        w: Optional[tk.Misc] = widget
        while w is not None:
            if isinstance(w, ScrolledFrame):
                return w
            w = getattr(w, "master", None)
        return None

    def _dispatch_wheel(self, event: tk.Event) -> None:
        sf = self._scrolled_frame_under(event.widget)
        if sf is not self:
            return
        delta = getattr(event, "delta", 0)
        if delta:
            sf.canvas.yview_scroll(int(-1 * (delta / 120)), "units")

    def _dispatch_wheel_up(self, event: tk.Event) -> None:
        sf = self._scrolled_frame_under(event.widget)
        if sf is self:
            sf.canvas.yview_scroll(-1, "units")

    def _dispatch_wheel_down(self, event: tk.Event) -> None:
        sf = self._scrolled_frame_under(event.widget)
        if sf is self:
            sf.canvas.yview_scroll(1, "units")
