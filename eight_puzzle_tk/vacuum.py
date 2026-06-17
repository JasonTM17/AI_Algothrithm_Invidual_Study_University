"""Vacuum-cleaner game + graph-coloring CSP demo for the desktop app.

This tab is intentionally separate from the 8-puzzle solver. It demonstrates a
classic AI agent environment (vacuum world) and uses graph coloring as a CSP
for cleaning-batch scheduling, which is a better academic fit than pretending
graph coloring solves the 8-puzzle path problem.
"""

from __future__ import annotations

import random
import tkinter as tk
from collections import deque
from tkinter import ttk
from typing import Any, Dict, Iterable, List, Set

from .theme import PALETTE


ROWS = 2
COLS = 3
ROOM_NAMES = ("A", "B", "C", "D", "E", "F")
DEFAULT_DIRTY = {1, 2, 4, 5}
SLOT_COLORS = ("#bfdbfe", "#fde68a", "#bbf7d0", "#fecaca")


def room_neighbors(room: int) -> List[int]:
    """Return orthogonal neighboring room indices."""
    row, col = divmod(room, COLS)
    result: List[int] = []
    if row > 0:
        result.append(room - COLS)
    if row < ROWS - 1:
        result.append(room + COLS)
    if col > 0:
        result.append(room - 1)
    if col < COLS - 1:
        result.append(room + 1)
    return result


def greedy_room_coloring(dirty_rooms: Iterable[int]) -> Dict[int, int]:
    """Greedy graph coloring for dirty rooms.

    Nodes are rooms; edges connect adjacent rooms. A color is interpreted as a
    cleaning time slot/batch, so adjacent dirty rooms are not assigned the same
    slot.
    """
    dirty = sorted(set(dirty_rooms))
    colors: Dict[int, int] = {}
    for room in dirty:
        used = {colors[n] for n in room_neighbors(room) if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[room] = color
    return colors


def shortest_room_path(start: int, goal: int) -> List[int]:
    """Shortest path of room indices from start to goal, inclusive."""
    if start == goal:
        return [start]
    queue: deque[List[int]] = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        for nxt in room_neighbors(path[-1]):
            if nxt in seen:
                continue
            new_path = path + [nxt]
            if nxt == goal:
                return new_path
            seen.add(nxt)
            queue.append(new_path)
    return [start]


def _cell_label(app: Any, room: int) -> str:
    parts = [ROOM_NAMES[room]]
    if room == app.vacuum_position:
        parts.append("VAC")
    parts.append("DIRTY" if room in app.vacuum_dirty else "CLEAN")
    if room in app.vacuum_coloring:
        parts.append(f"Slot {app.vacuum_coloring[room] + 1}")
    return "\n".join(parts)


def build_vacuum_tab(parent: tk.Misc, app: Any) -> None:
    """Build the vacuum-cleaner game tab and store widget refs on app."""
    app.vacuum_position = 0
    app.vacuum_dirty: Set[int] = set(DEFAULT_DIRTY)
    app.vacuum_coloring: Dict[int, int] = {}
    app.vacuum_actions = 0

    title = ttk.Label(parent, text=app._t("vacuum_title"), font=("Segoe UI", 12, "bold"))
    title.pack(anchor=tk.W, pady=(0, 6))
    app._i18n_labels["vacuum_title"] = title

    note = ttk.Label(
        parent,
        text=app._t("vacuum_note"),
        wraplength=920,
        justify=tk.LEFT,
    )
    note.pack(anchor=tk.W, pady=(0, 8))
    app._i18n_labels["vacuum_note"] = note

    body = ttk.Frame(parent)
    body.pack(fill=tk.BOTH, expand=True)

    left = ttk.LabelFrame(body, text=app._t("vacuum_game"), padding=8)
    left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
    app.vacuum_cells: List[tk.Button] = []
    grid = ttk.Frame(left, style="Card.TFrame")
    grid.pack()
    for room in range(ROWS * COLS):
        cell = tk.Button(
            grid,
            width=12,
            height=4,
            font=("Consolas", 11, "bold"),
            command=lambda r=room: toggle_vacuum_dirt(app, r),
        )
        cell.grid(row=room // COLS, column=room % COLS, padx=4, pady=4)
        app.vacuum_cells.append(cell)

    app.vacuum_status_var = tk.StringVar(value="")
    ttk.Label(left, textvariable=app.vacuum_status_var, style="Muted.TLabel", wraplength=360).pack(
        anchor=tk.W, pady=(8, 0)
    )

    controls = ttk.Frame(left, style="Card.TFrame")
    controls.pack(pady=(8, 0))
    app._i18n_labels["vacuum_up"] = ttk.Button(
        controls, text=app._t("vacuum_up"), command=lambda: move_vacuum(app, "Up")
    )
    app._i18n_labels["vacuum_up"].grid(row=0, column=1, padx=2, pady=2)
    app._i18n_labels["vacuum_left"] = ttk.Button(
        controls, text=app._t("vacuum_left"), command=lambda: move_vacuum(app, "Left")
    )
    app._i18n_labels["vacuum_left"].grid(row=1, column=0, padx=2, pady=2)
    app._i18n_labels["vacuum_suck"] = ttk.Button(
        controls, text=app._t("vacuum_suck"), command=lambda: suck_current_room(app)
    )
    app._i18n_labels["vacuum_suck"].grid(row=1, column=1, padx=2, pady=2)
    app._i18n_labels["vacuum_right"] = ttk.Button(
        controls, text=app._t("vacuum_right"), command=lambda: move_vacuum(app, "Right")
    )
    app._i18n_labels["vacuum_right"].grid(row=1, column=2, padx=2, pady=2)
    app._i18n_labels["vacuum_down"] = ttk.Button(
        controls, text=app._t("vacuum_down"), command=lambda: move_vacuum(app, "Down")
    )
    app._i18n_labels["vacuum_down"].grid(row=2, column=1, padx=2, pady=2)

    actions = ttk.Frame(left, style="Card.TFrame")
    actions.pack(fill=tk.X, pady=(8, 0))
    app._i18n_labels["vacuum_reset"] = ttk.Button(
        actions, text=app._t("vacuum_reset"), command=lambda: reset_vacuum(app)
    )
    app._i18n_labels["vacuum_reset"].grid(row=0, column=0, sticky="ew", padx=2, pady=2)
    app._i18n_labels["vacuum_random"] = ttk.Button(
        actions, text=app._t("vacuum_random"), command=lambda: randomize_vacuum(app)
    )
    app._i18n_labels["vacuum_random"].grid(row=0, column=1, sticky="ew", padx=2, pady=2)
    app._i18n_labels["vacuum_color_plan"] = ttk.Button(
        actions, text=app._t("vacuum_color_plan"), command=lambda: color_vacuum_rooms(app)
    )
    app._i18n_labels["vacuum_color_plan"].grid(row=1, column=0, sticky="ew", padx=2, pady=2)
    app._i18n_labels["vacuum_auto_clean"] = ttk.Button(
        actions, text=app._t("vacuum_auto_clean"), command=lambda: auto_clean_vacuum(app)
    )
    app._i18n_labels["vacuum_auto_clean"].grid(row=1, column=1, sticky="ew", padx=2, pady=2)
    actions.columnconfigure(0, weight=1)
    actions.columnconfigure(1, weight=1)

    right = ttk.Frame(body)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    peas = ttk.LabelFrame(right, text=app._t("vacuum_peas"), padding=8)
    peas.pack(fill=tk.X)
    app.vacuum_peas_var = tk.StringVar(value=app._t("vacuum_peas_text"))
    ttk.Label(peas, textvariable=app.vacuum_peas_var, wraplength=720, justify=tk.LEFT).pack(anchor=tk.W)

    coloring = ttk.LabelFrame(right, text=app._t("vacuum_coloring"), padding=8)
    coloring.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    app.vacuum_coloring_note_var = tk.StringVar(value=app._t("vacuum_coloring_note"))
    ttk.Label(
        coloring,
        textvariable=app.vacuum_coloring_note_var,
        wraplength=720,
        justify=tk.LEFT,
    ).pack(anchor=tk.W, pady=(0, 6))

    cols = ("Room", "Dirty?", "Neighbors", "Color slot")
    tree = ttk.Treeview(coloring, columns=cols, show="headings", height=8)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=140 if col != "Neighbors" else 220, anchor=tk.W)
    tree.pack(fill=tk.BOTH, expand=True)
    app.vacuum_tree = tree

    refresh_vacuum(app, app._t("vacuum_ready"))


def refresh_vacuum(app: Any, status: str = "") -> None:
    """Refresh board cells, status, and coloring table."""
    for room, cell in enumerate(app.vacuum_cells):
        slot = app.vacuum_coloring.get(room)
        if room == app.vacuum_position:
            bg = PALETTE["primary"]
            fg = "#ffffff"
        elif room in app.vacuum_dirty and slot is not None:
            bg = SLOT_COLORS[slot % len(SLOT_COLORS)]
            fg = PALETTE["text"]
        elif room in app.vacuum_dirty:
            bg = "#fee2e2"
            fg = PALETTE["text"]
        else:
            bg = "#ecfdf5"
            fg = PALETTE["text"]
        cell.configure(text=_cell_label(app, room), bg=bg, fg=fg, activebackground=PALETTE["cell_hover"])

    dirty_count = len(app.vacuum_dirty)
    if dirty_count == 0:
        app.vacuum_status_var.set(app._t("vacuum_goal").format(actions=app.vacuum_actions))
    else:
        app.vacuum_status_var.set(
            status
            or app._t("vacuum_status").format(
                room=ROOM_NAMES[app.vacuum_position],
                dirty=dirty_count,
                actions=app.vacuum_actions,
            )
        )
    populate_coloring_table(app)


def populate_coloring_table(app: Any) -> None:
    """Render the dirty-room graph-coloring assignment."""
    tree = app.vacuum_tree
    tree.delete(*tree.get_children())
    for room in range(ROWS * COLS):
        neighbors = ", ".join(ROOM_NAMES[n] for n in room_neighbors(room))
        slot = app.vacuum_coloring.get(room)
        tree.insert(
            "",
            tk.END,
            values=(
                ROOM_NAMES[room],
                "yes" if room in app.vacuum_dirty else "no",
                neighbors,
                "-" if slot is None else f"slot {slot + 1}",
            ),
        )


def toggle_vacuum_dirt(app: Any, room: int) -> None:
    """Clicking a room toggles dirt so teachers can create examples live."""
    if room in app.vacuum_dirty:
        app.vacuum_dirty.remove(room)
    else:
        app.vacuum_dirty.add(room)
    app.vacuum_coloring = {}
    refresh_vacuum(app, app._t("vacuum_toggled").format(room=ROOM_NAMES[room]))


def move_vacuum(app: Any, action: str) -> None:
    """Move the vacuum if the action is legal."""
    row, col = divmod(app.vacuum_position, COLS)
    target = app.vacuum_position
    if action == "Up" and row > 0:
        target -= COLS
    elif action == "Down" and row < ROWS - 1:
        target += COLS
    elif action == "Left" and col > 0:
        target -= 1
    elif action == "Right" and col < COLS - 1:
        target += 1
    else:
        refresh_vacuum(app, app._t("vacuum_illegal"))
        return
    app.vacuum_position = target
    app.vacuum_actions += 1
    refresh_vacuum(app)


def suck_current_room(app: Any) -> None:
    """Clean the current room."""
    app.vacuum_actions += 1
    if app.vacuum_position in app.vacuum_dirty:
        app.vacuum_dirty.remove(app.vacuum_position)
        app.vacuum_coloring = {}
        refresh_vacuum(app, app._t("vacuum_cleaned").format(room=ROOM_NAMES[app.vacuum_position]))
    else:
        refresh_vacuum(app, app._t("vacuum_already_clean").format(room=ROOM_NAMES[app.vacuum_position]))


def reset_vacuum(app: Any) -> None:
    app.vacuum_position = 0
    app.vacuum_dirty = set(DEFAULT_DIRTY)
    app.vacuum_coloring = {}
    app.vacuum_actions = 0
    refresh_vacuum(app, app._t("vacuum_ready"))


def randomize_vacuum(app: Any) -> None:
    dirty = {room for room in range(ROWS * COLS) if random.random() < 0.55}
    if not dirty:
        dirty.add(random.randrange(ROWS * COLS))
    app.vacuum_position = random.randrange(ROWS * COLS)
    app.vacuum_dirty = dirty
    app.vacuum_coloring = {}
    app.vacuum_actions = 0
    refresh_vacuum(app, app._t("vacuum_randomized"))


def color_vacuum_rooms(app: Any) -> None:
    app.vacuum_coloring = greedy_room_coloring(app.vacuum_dirty)
    slots = 0 if not app.vacuum_coloring else max(app.vacuum_coloring.values()) + 1
    refresh_vacuum(app, app._t("vacuum_colored").format(slots=slots))


def auto_clean_vacuum(app: Any) -> None:
    """Simple deterministic vacuum policy: nearest dirty room, then SUCK."""
    plan: List[str] = []
    while app.vacuum_dirty:
        if app.vacuum_position in app.vacuum_dirty:
            app.vacuum_dirty.remove(app.vacuum_position)
            app.vacuum_actions += 1
            plan.append(f"Suck {ROOM_NAMES[app.vacuum_position]}")
            continue
        target = min(
            app.vacuum_dirty,
            key=lambda room: (len(shortest_room_path(app.vacuum_position, room)), room),
        )
        path = shortest_room_path(app.vacuum_position, target)
        for room in path[1:]:
            app.vacuum_position = room
            app.vacuum_actions += 1
            plan.append(f"Move {ROOM_NAMES[room]}")
        app.vacuum_dirty.remove(app.vacuum_position)
        app.vacuum_actions += 1
        plan.append(f"Suck {ROOM_NAMES[app.vacuum_position]}")
    app.vacuum_coloring = {}
    refresh_vacuum(app, app._t("vacuum_auto_done").format(steps=len(plan)))
