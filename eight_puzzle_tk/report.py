"""Coursework submission pack: build + preview + save Markdown report.

The Report tab uses the most recent successful sidebar run (stored on
``app.last_result``) to assemble a full submission pack via
:func:`build_submission_pack`. The Markdown is shown in a scrollable Text
widget. The user can copy or save the report to disk.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any, Dict, Optional

from eight_puzzle_search_app import build_submission_pack


def build_report_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Report tab widgets and store refs on ``app``."""
    app._i18n_labels["report_title"] = ttk.Label(
        parent, text=app._t("report_title"), font=("", 12, "bold"),
    )
    app._i18n_labels["report_title"].pack(anchor=tk.W, pady=(0, 6))

    app.report_status_var = tk.StringVar(value=app._t("report_idle"))
    ttk.Label(parent, textvariable=app.report_status_var).pack(anchor=tk.W)

    bar = ttk.Frame(parent)
    bar.pack(fill=tk.X, pady=(6, 4))
    app._i18n_labels["report_generate"] = ttk.Button(
        bar, text=app._t("report_generate"), command=app._on_report_generate,
    )
    app._i18n_labels["report_generate"].pack(side=tk.LEFT)
    app._i18n_labels["report_save"] = ttk.Button(
        bar, text=app._t("report_save"), command=app._on_report_save,
    )
    app._i18n_labels["report_save"].pack(side=tk.LEFT, padx=4)
    app._i18n_labels["report_copy"] = ttk.Button(
        bar, text=app._t("report_copy"), command=app._on_report_copy,
    )
    app._i18n_labels["report_copy"].pack(side=tk.LEFT, padx=4)

    preview_frame = ttk.LabelFrame(
        parent, text=app._t("report_preview"), padding=8,
    )
    preview_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    text = tk.Text(
        preview_frame, wrap=tk.NONE, height=24,
        font=("Consolas", 9), state=tk.DISABLED,
    )
    yscroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=text.yview)
    xscroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=text.xview)
    text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    text.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")
    preview_frame.rowconfigure(0, weight=1)
    preview_frame.columnconfigure(0, weight=1)
    app.report_text = text
    app.report_last_pack: Optional[Dict[str, Any]] = None


def populate_report_tab(app: Any, pack: Dict[str, Any]) -> None:
    """Show the Markdown body of the pack in the preview widget."""
    app.report_text.configure(state=tk.NORMAL)
    app.report_text.delete("1.0", tk.END)
    app.report_text.insert("1.0", pack.get("markdown", ""))
    app.report_text.configure(state=tk.DISABLED)
    app.report_last_pack = pack
    app.report_status_var.set(
        app._t("report_built").format(
            title=pack.get("title", ""),
            lines=pack.get("markdown", "").count("\n") + 1,
        )
    )


def reset_report_tab(app: Any) -> None:
    """Clear the Report tab to its idle state."""
    app.report_text.configure(state=tk.NORMAL)
    app.report_text.delete("1.0", tk.END)
    app.report_text.configure(state=tk.DISABLED)
    app.report_last_pack = None
    app.report_status_var.set(app._t("report_idle"))


def on_report_generate(app: Any) -> None:
    """Report tab 'Generate' button: build a submission pack from the last run."""
    if app.last_result is None or app.last_certificate is None:
        app.report_status_var.set(app._t("report_no_run"))
        return
    try:
        pack = build_submission_pack(
            app.last_result,
            app.last_heuristic or "manhattan",
            app.last_certificate,
        )
    except Exception as exc:
        app.report_status_var.set(
            f"report_failed ({type(exc).__name__}): {exc}"
        )
        return
    populate_report_tab(app, pack)


def on_report_save(app: Any) -> None:
    """Report tab 'Save to file' button: write the Markdown to a user-chosen path."""
    pack = getattr(app, "report_last_pack", None)
    if pack is None:
        app.report_status_var.set(app._t("report_no_pack"))
        return
    path = filedialog.asksaveasfilename(
        parent=app.root,
        defaultextension=".md",
        filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All", "*.*")],
        initialfile=f"{pack.get('title', 'report').replace(' ', '_').replace('/', '-')}.md",
    )
    if not path:
        return
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(pack.get("markdown", ""))
    app.report_status_var.set(app._t("report_saved").format(path=path))


def on_report_copy(app: Any) -> None:
    """Report tab 'Copy' button: copy the Markdown body to the clipboard."""
    pack = getattr(app, "report_last_pack", None)
    if pack is None:
        app.report_status_var.set(app._t("report_no_pack"))
        return
    app.root.clipboard_clear()
    app.root.clipboard_append(pack.get("markdown", ""))
    app.report_status_var.set(app._t("report_copied"))
