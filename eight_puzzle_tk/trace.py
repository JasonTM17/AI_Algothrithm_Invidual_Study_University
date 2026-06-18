"""Render SearchResult.trace_rows into a scrollable Tkinter Treeview plus an
interactive replay player that scrubs through individual trace rows.

The trace is a read-only step log: one row per expansion, columns from
``eight_puzzle_search_app.TRACE_COLUMNS``. Column headings are kept in English
because they match the technical vocabulary in the core module; titles and
status messages are translated via the app's bilingual i18n.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple

from eight_puzzle_search_app import TRACE_COLUMNS, SearchResult, State

from .theme import PALETTE


# Tuned for the 8-puzzle state strings emitted by the core module.
_COL_WIDTHS: dict = {
    "Step": 50, "Algorithm": 90, "Node": 60, "Action": 70, "Depth": 50,
    "g": 40, "h": 40, "f": 40,
    "Priority Rule": 100, "Selection Key": 100,
    "Generated Children": 160, "Skipped States": 130,
    "Frontier": 160, "Reached": 140, "Decision/Note": 200,
}
_RIGHT_ALIGNED = {"Step", "Depth", "g", "h", "f"}

_CELL_FONT = ("Consolas", 28, "bold")


# ---------------------------------------------------------------------------
# Helpers for parsing the Node field into a 9-tuple
# ---------------------------------------------------------------------------

def _parse_node_to_state(node_text: str) -> Optional[State]:
    """Parse a multiline board-string like ``1 2 3\\n4 5 6\\n7 8 0`` into a 9-tuple."""
    chars = node_text.replace("\n", " ").split()
    if len(chars) != 9:
        return None
    try:
        return tuple(int(c) for c in chars)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 3x3 board widget reused from playback.py style
# ---------------------------------------------------------------------------

def _make_board(parent: tk.Misc) -> List[tk.Label]:
    """Build a 3x3 grid of bordered Labels for trace replay."""
    border = tk.Frame(parent, bg=PALETTE["border"], bd=0)
    border.pack(anchor=tk.CENTER, padx=3, pady=3)
    cells: List[tk.Label] = []
    inner = tk.Frame(border, bg=PALETTE["border"], bd=0)
    inner.pack(padx=2, pady=2)
    for i in range(9):
        lbl = tk.Label(
            inner, text="-", width=4, height=1,
            font=_CELL_FONT, relief=tk.FLAT, borderwidth=0,
            bg=PALETTE["tile_bg"], fg=PALETTE["text"],
        )
        lbl.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="nsew")
        cells.append(lbl)
    for r in range(3):
        inner.rowconfigure(r, weight=1, uniform="trace_cell", minsize=60)
    for c in range(3):
        inner.columnconfigure(c, weight=1, uniform="trace_cell", minsize=60)
    return cells


def _render_board(cells: List[tk.Label], state: State) -> None:
    """Update the 3x3 labels to show *state* (0 = blank)."""
    for i, value in enumerate(state):
        is_blank = value == 0
        cells[i].config(
            text="" if is_blank else str(value),
            bg=PALETTE["blank_tile_bg"] if is_blank else PALETTE["tile_bg"],
            fg=PALETTE["blank_tile_fg"] if is_blank else PALETTE["text"],
        )


# ---------------------------------------------------------------------------
# Info chip (metric-card style from results.py)
# ---------------------------------------------------------------------------

def _make_info_chip(parent: tk.Misc, label_text: str, var: tk.Variable) -> tk.Frame:
    """Build a small metric card: muted label on top, bold value below."""
    card = tk.Frame(
        parent, bg=PALETTE["card_bg"],
        highlightbackground=PALETTE["border"],
        highlightthickness=1, padx=12, pady=8,
    )
    tk.Label(
        card, text=label_text, font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(anchor=tk.W)
    tk.Label(
        card, textvariable=var, font=("Segoe UI", 18, "bold"),
        fg=PALETTE["text"], bg=PALETTE["card_bg"],
    ).pack(anchor=tk.W, pady=(2, 0))
    return card


def _make_text_row(parent: tk.Misc, label_text: str, var: tk.StringVar) -> tk.Frame:
    """Build a row with label + value, muted label inline."""
    row = tk.Frame(parent, bg=PALETTE["card_bg"])
    tk.Label(
        row, text=label_text, font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT)
    tk.Label(
        row, textvariable=var, font=("Segoe UI", 10, "bold"),
        fg=PALETTE["text"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT, padx=(4, 20))
    return row


# ---------------------------------------------------------------------------
# Trace replay player section
# ---------------------------------------------------------------------------

def build_trace_replay_section(parent: tk.Misc, app: Any) -> None:
    """Create the trace replay player widgets, stored on ``app`` but hidden.

    The section is packed only when :func:`populate_trace_replay` loads
    trace data, and hidden again by :func:`reset_trace_replay`.
    """

    # --- Vars exposed on app per spec -----------------------------------
    app.replay_step_var = tk.IntVar(value=0)
    app.replay_gn = tk.StringVar(value="-")
    app.replay_hn = tk.StringVar(value="-")
    app.replay_fn = tk.StringVar(value="-")
    app.replay_priority = tk.StringVar(value="-")
    app.replay_key = tk.StringVar(value="-")
    app.replay_generated = tk.StringVar(value="-")
    app.replay_skipped = tk.StringVar(value="-")

    # Hidden container
    app.trace_replay_container = tk.LabelFrame(
        parent, text=app._t("trace_replay_title"),
        font=("Segoe UI", 10, "bold"),
        fg=PALETTE["primary"], bg=PALETTE["card_bg"],
        padx=12, pady=10,
    )

    # ---- Top part: board + info chips in a horizontal row ---------------
    top_row = tk.Frame(app.trace_replay_container, bg=PALETTE["card_bg"])
    top_row.pack(fill=tk.X)

    # Board on the left
    board_frame = tk.LabelFrame(
        top_row,
        text=app._t("trace_replay_state"),
        font=("Segoe UI", 9, "bold"),
        fg=PALETTE["primary"], bg=PALETTE["card_bg"],
        padx=8, pady=6,
    )
    board_frame.pack(side=tk.LEFT, padx=(0, 16))
    app.trace_replay_cells = _make_board(board_frame)

    # Info chips on the right (2x2 grid: g, h / f, step)
    chips_container = tk.Frame(top_row, bg=PALETTE["card_bg"])
    chips_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    chip_grid = tk.Frame(chips_container, bg=PALETTE["card_bg"])
    chip_grid.pack(anchor=tk.W)

    _make_info_chip(chip_grid, "g(n)", app.replay_gn).grid(
        row=0, column=0, padx=3, pady=3, sticky="nsew",
    )
    _make_info_chip(chip_grid, "h(n)", app.replay_hn).grid(
        row=0, column=1, padx=3, pady=3, sticky="nsew",
    )
    _make_info_chip(chip_grid, "f(n)", app.replay_fn).grid(
        row=1, column=0, padx=3, pady=3, sticky="nsew",
    )
    _make_info_chip(chip_grid, "Step", app.replay_step_var).grid(
        row=1, column=1, padx=3, pady=3, sticky="nsew",
    )

    # ---- Middle rows: Priority, Key, Generated, Skipped -----------------
    detail_frame = tk.Frame(app.trace_replay_container, bg=PALETTE["card_bg"])
    detail_frame.pack(fill=tk.X, pady=(8, 0))

    row_a = tk.Frame(detail_frame, bg=PALETTE["card_bg"])
    row_a.pack(fill=tk.X, pady=2)
    tk.Label(
        row_a, text="Priority Rule", font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT)
    tk.Label(
        row_a, textvariable=app.replay_priority,
        font=("Segoe UI", 10, "bold"),
        fg=PALETTE["text"], bg=PALETTE["card_bg"], wraplength=300,
    ).pack(side=tk.LEFT, padx=(6, 24))

    tk.Label(
        row_a, text="Selection Key", font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT)
    tk.Label(
        row_a, textvariable=app.replay_key,
        font=("Segoe UI", 10, "bold"),
        fg=PALETTE["primary"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT, padx=(6, 0))

    row_b = tk.Frame(detail_frame, bg=PALETTE["card_bg"])
    row_b.pack(fill=tk.X, pady=2)
    tk.Label(
        row_b, text="Generated Children", font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT)
    tk.Label(
        row_b, textvariable=app.replay_generated,
        font=("Segoe UI", 10, "bold"),
        fg=PALETTE["ok"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT, padx=(6, 24))

    tk.Label(
        row_b, text="Skipped States", font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT)
    tk.Label(
        row_b, textvariable=app.replay_skipped,
        font=("Segoe UI", 10, "bold"),
        fg=PALETTE["warn"], bg=PALETTE["card_bg"],
    ).pack(side=tk.LEFT, padx=(6, 0))

    # ---- Slider at the bottom -------------------------------------------
    slider_frame = tk.Frame(app.trace_replay_container, bg=PALETTE["card_bg"])
    slider_frame.pack(fill=tk.X, pady=(10, 0))

    tk.Label(
        slider_frame, text="Row", font=("Segoe UI", 9),
        fg=PALETTE["muted"], bg=PALETTE["card_bg"],
    ).pack(anchor=tk.W)

    slider_inner = tk.Frame(slider_frame, bg=PALETTE["card_bg"])
    slider_inner.pack(fill=tk.X, pady=(2, 0))

    app.trace_replay_slider = ttk.Scale(
        slider_inner, from_=0, to=1, orient=tk.HORIZONTAL,
        variable=app.replay_step_var,
        command=lambda _v: _on_trace_replay_slider(app),
    )
    app.trace_replay_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

    app.trace_replay_slider_value = tk.Label(
        slider_inner, textvariable=app.replay_step_var,
        font=("Segoe UI", 10, "bold"),
        fg=PALETTE["text"], bg=PALETTE["card_bg"], width=5, anchor=tk.E,
    )
    app.trace_replay_slider_value.pack(side=tk.LEFT, padx=(8, 0))

    # Store trace data for replay
    app._trace_replay_rows: List[Dict[str, Any]] = []


def _on_trace_replay_slider(app: Any) -> None:
    """Slider callback: render the selected trace row's state and data."""
    idx = app.replay_step_var.get()
    rows = app._trace_replay_rows
    if not rows or idx < 0 or idx >= len(rows):
        return
    _render_trace_row(app, rows[idx], idx)


def _render_trace_row(app: Any, row: Dict[str, Any], idx: int) -> None:
    """Update all replay widgets from a single trace row dictionary."""
    # Board
    node_text = str(row.get("Node", ""))
    state = _parse_node_to_state(node_text)
    if state is not None:
        _render_board(app.trace_replay_cells, state)

    # Numeric chips
    app.replay_gn.set(str(row.get("g", "-")))
    app.replay_hn.set(str(row.get("h", "-")))
    app.replay_fn.set(str(row.get("f", "-")))
    app.replay_step_var.set(idx)

    # Text fields
    priority = str(row.get("Priority Rule", ""))
    app.replay_priority.set(priority if priority else "-")
    key = str(row.get("Selection Key", ""))
    app.replay_key.set(key if key else "-")
    gen = row.get("Generated Children")
    app.replay_generated.set(str(gen) if gen not in (None, "") else "-")
    skip = row.get("Skipped States")
    app.replay_skipped.set(str(skip) if skip not in (None, "") else "-")


def populate_trace_replay(app: Any, rows: List[Dict[str, Any]]) -> None:
    """Load trace rows into the replay player and show the section."""
    app._trace_replay_rows = list(rows)
    count = len(rows)
    if count == 0:
        app.trace_replay_container.pack_forget()
        return

    # Configure slider range
    app.trace_replay_slider.configure(from_=0, to=max(0, count - 1))
    app.replay_step_var.set(0)

    # Render first row
    _render_trace_row(app, rows[0], 0)

    # Show the section
    if not app.trace_replay_container.winfo_ismapped():
        app.trace_replay_container.pack(fill=tk.X, pady=(0, 8))
        # Re-pack order: ensure container is before title/status/tree
        app.trace_replay_container.lift()


def reset_trace_replay(app: Any) -> None:
    """Clear replay player and hide the section."""
    app._trace_replay_rows = []
    app.replay_step_var.set(0)
    app.replay_gn.set("-")
    app.replay_hn.set("-")
    app.replay_fn.set("-")
    app.replay_priority.set("-")
    app.replay_key.set("-")
    app.replay_generated.set("-")
    app.replay_skipped.set("-")
    for c in app.trace_replay_cells:
        c.config(text="-", bg=PALETTE["tile_bg"], fg=PALETTE["text"])
    app.trace_replay_slider.configure(to=1)
    if app.trace_replay_container.winfo_ismapped():
        app.trace_replay_container.pack_forget()


# ---------------------------------------------------------------------------
# Main tab builder + populate / reset
# ---------------------------------------------------------------------------

def build_trace_story_section(parent: tk.Misc, app: Any) -> None:
    """Build a hidden 'Why This Node?' section that explains each trace row."""
    app.trace_story_container = ttk.LabelFrame(
        parent, text=app._t("trace_story_title"),
        padding=10,
    )

    intro = ttk.Label(
        app.trace_story_container,
        text=app._t("trace_story_subtitle"),
        foreground=PALETTE["muted"], wraplength=680, justify=tk.LEFT,
    )
    intro.pack(anchor=tk.W)

    app.trace_story_text = tk.Text(
        app.trace_story_container, height=8, wrap=tk.WORD,
        font=("Segoe UI", 10), bg=PALETTE["card_bg"], fg=PALETTE["text"],
        state=tk.DISABLED, relief=tk.FLAT, borderwidth=0,
        highlightthickness=0, padx=4, pady=4,
    )
    app.trace_story_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))


def _build_story_for(algorithm: str, row: Dict[str, Any]) -> str:
    """Generate a 'Why this node?' explanation from a single trace row + algorithm."""
    g = row.get("g", "?")
    h = row.get("h", "?")
    f = row.get("f", "?")
    depth = row.get("Depth", "?")
    key = row.get("Selection Key", "")
    algo = (algorithm or "").lower()
    lines: List[str] = []
    if "bfs" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: BFS picks the shallowest unexplored "
            f"node (depth {depth}). Selection key = {key}."
        )
    elif "dfs" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: DFS dives into the deepest branch. "
            f"Node at depth {depth} was popped from the LIFO stack."
        )
    elif "ucs" in algo or "uniform" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: UCS picks the node with the lowest "
            f"g(n) = {g}. Selection key = {key}."
        )
    elif "ida" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: IDA* uses DFS bounded by f-cost "
            f"threshold. f(n) = {f}, threshold = {key}."
        )
    elif "a*" in algo or "astar" in algo or "a star" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: A* picks the node with the lowest "
            f"f(n) = g(n) + h(n) = {g} + {h} = {f}. Selection key = {key}."
        )
    elif "greedy" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: Greedy picks the node with the "
            f"lowest h(n) = {h}. Selection key = {key}."
        )
    elif "hill" in algo or "climbing" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: Hill Climbing moves to the neighbor "
            f"with the lowest h(n) = {h}."
        )
    elif "beam" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: Local Beam Search keeps the top-k "
            f"states by h(n) = {h}."
        )
    elif "anneal" in algo:
        lines.append(
            f"Step {row.get('Step', '?')}: Simulated Annealing accepts a "
            f"neighbor at temperature {key} based on h(n) = {h}."
        )
    else:
        lines.append(
            f"Step {row.get('Step', '?')}: Algorithm '{algorithm}' selects "
            f"the next node using g = {g}, h = {h}, f = {f}."
        )
    note = row.get("Decision/Note", "")
    if note:
        lines.append(f"   Note: {note}")
    return " ".join(lines)


def build_search_tree_section(parent: tk.Misc, app: Any) -> None:
    """Build a hidden search tree preview section that lists explored nodes."""
    app.tree_preview_container = ttk.LabelFrame(
        parent, text=app._t("trace_tree_title"),
        padding=10,
    )
    app.tree_preview_intro = ttk.Label(
        app.tree_preview_container,
        text=app._t("trace_tree_subtitle"),
        foreground=PALETTE["muted"], wraplength=680, justify=tk.LEFT,
    )
    app.tree_preview_intro.pack(anchor=tk.W)
    app.tree_preview_grid = tk.Frame(app.tree_preview_container, bg=PALETTE["card_bg"])
    app.tree_preview_grid.pack(fill=tk.X, expand=True, pady=(8, 0))
    app._tree_preview_cards: List[tk.Frame] = []


def _populate_search_tree(app: Any, rows: List[Dict[str, Any]]) -> None:
    """Render a small grid of board cards for the first N trace rows."""
    for card in app._tree_preview_cards:
        card.destroy()
    app._tree_preview_cards = []
    if not rows:
        return
    max_nodes = min(len(rows), 12)
    cols = 4
    for idx in range(max_nodes):
        row_data = rows[idx]
        node_text = str(row_data.get("Node", ""))
        state = _parse_node_to_state(node_text)
        card = tk.Frame(
            app.tree_preview_grid,
            bg=PALETTE["card_bg"],
            highlightbackground=PALETTE["primary" if idx == 0 else "border"],
            highlightthickness=1, padx=4, pady=4,
        )
        card.grid(
            row=idx // cols, column=idx % cols,
            padx=4, pady=4, sticky="nsew",
        )
        app._tree_preview_cards.append(card)

        # Small board
        mini = _make_board(card)
        if state is not None:
            _render_board(mini, state)

        # Caption
        step = row_data.get("Step", idx)
        g = row_data.get("g", "-")
        h = row_data.get("h", "-")
        tk.Label(
            card, text=f"#{step}  g={g} h={h}",
            font=("Segoe UI", 8), fg=PALETTE["muted"], bg=PALETTE["card_bg"],
        ).pack(anchor=tk.W, pady=(2, 0))
    for c in range(cols):
        app.tree_preview_grid.columnconfigure(c, weight=1, uniform="tree_node")


def build_trace_tab(parent: tk.Misc, app: Any) -> None:
    """Create the Trace tab widgets and store the Treeview on ``app``."""
    # Trace replay player (hidden until trace data is available)
    build_trace_replay_section(parent, app)

    # Search tree preview (hidden until trace data is available)
    build_search_tree_section(parent, app)

    # Trace story / Why This Node? (hidden until trace data is available)
    build_trace_story_section(parent, app)

    app._i18n_labels["trace_title"] = ttk.Label(
        parent, text=app._t("trace_title"), style="CardHeading.TLabel",
    )
    app._i18n_labels["trace_title"].pack(anchor=tk.W, pady=(0, 4))

    app.trace_status_var = tk.StringVar(value=app._t("trace_idle"))
    tk.Label(
        parent, textvariable=app.trace_status_var,
        font=("Segoe UI", 10), bg=PALETTE["card_bg"], fg=PALETTE["muted"],
    ).pack(anchor=tk.W)

    tree_frame = tk.Frame(parent, bg=PALETTE["card_bg"])
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    tree = ttk.Treeview(
        tree_frame, columns=TRACE_COLUMNS, show="headings", height=12,
    )
    for col in TRACE_COLUMNS:
        tree.heading(col, text=col)
        tree.column(
            col,
            width=_COL_WIDTHS.get(col, 80),
            anchor=tk.E if col in _RIGHT_ALIGNED else tk.W,
            stretch=False,
        )
    app.trace_tree = tree

    vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)


def populate_trace_tab(app: Any, result: SearchResult) -> None:
    """Refresh the Trace Treeview from ``result.trace_rows``."""
    tree = app.trace_tree
    tree.delete(*tree.get_children())
    if not result.trace_rows:
        app.trace_status_var.set(app._t("trace_empty"))
        reset_trace_replay(app)
        reset_trace_story(app)
        reset_search_tree(app)
        return
    for row in result.trace_rows:
        values = [str(row.get(col, "")) for col in TRACE_COLUMNS]
        tree.insert("", tk.END, values=values)
    app.trace_status_var.set(f"{len(result.trace_rows)} rows")

    # Populate the replay player
    populate_trace_replay(app, result.trace_rows)

    # Populate the search tree preview
    if not app.tree_preview_container.winfo_ismapped():
        app.tree_preview_container.pack(fill=tk.X, pady=(0, 8))
    _populate_search_tree(app, result.trace_rows)

    # Populate the trace story
    populate_trace_story(app, result)


def reset_trace_tab(app: Any) -> None:
    """Return the Trace tab to its idle state (used on pre-search errors)."""
    app.trace_tree.delete(*app.trace_tree.get_children())
    app.trace_status_var.set(app._t("trace_idle"))
    reset_trace_replay(app)
    reset_trace_story(app)
    reset_search_tree(app)


def populate_trace_story(app: Any, result: SearchResult) -> None:
    """Fill the trace story Text widget with per-row 'Why this node?' explanations."""
    algorithm = result.algorithm
    rows = result.trace_rows
    if not rows:
        return
    sample = rows[: min(15, len(rows))]
    story_text = "\n".join(_build_story_for(algorithm, r) for r in sample)
    if len(rows) > 15:
        story_text += f"\n\n... and {len(rows) - 15} more rows."
    app.trace_story_text.config(state=tk.NORMAL)
    app.trace_story_text.delete("1.0", tk.END)
    app.trace_story_text.insert(tk.END, story_text)
    app.trace_story_text.config(state=tk.DISABLED)
    if not app.trace_story_container.winfo_ismapped():
        app.trace_story_container.pack(fill=tk.BOTH, expand=True, pady=(0, 8))


def reset_trace_story(app: Any) -> None:
    """Clear the trace story and hide the section."""
    if hasattr(app, "trace_story_text"):
        app.trace_story_text.config(state=tk.NORMAL)
        app.trace_story_text.delete("1.0", tk.END)
        app.trace_story_text.config(state=tk.DISABLED)
    if hasattr(app, "trace_story_container") and app.trace_story_container.winfo_ismapped():
        app.trace_story_container.pack_forget()


def reset_search_tree(app: Any) -> None:
    """Clear the search tree preview and hide the section."""
    if hasattr(app, "_tree_preview_cards"):
        for card in app._tree_preview_cards:
            card.destroy()
        app._tree_preview_cards = []
    if hasattr(app, "tree_preview_container") and app.tree_preview_container.winfo_ismapped():
        app.tree_preview_container.pack_forget()
