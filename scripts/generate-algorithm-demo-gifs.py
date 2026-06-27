"""Generate deterministic animated GIFs from real algorithm runs."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import eight_puzzle_search_app as puzzle  # noqa: E402
from web.algorithm_demo_assets import ASSET_DIR, algorithm_demo_path  # noqa: E402


WIDTH, HEIGHT = 800, 450
DEMO_START = puzzle.DEMO_PRESETS["medium_10"]
DEMO_HEURISTIC = "manhattan"
DEMO_SEED = 7
BACKGROUND = "#f4f8fb"
INK = "#0f172a"
MUTED = "#64748b"
ACCENT = "#0f9688"
ACCENT_DARK = "#08756d"
ACCENT_SOFT = "#dff7f3"
LINE = "#dbe5ec"
PANEL = "#ffffff"
ROSE = "#e11d48"


def load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if sys.platform == "win32":
        candidates.extend(
            [
                Path("C:/Windows/Fonts/consolab.ttf" if mono and bold else "C:/Windows/Fonts/consola.ttf")
                if mono
                else Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
            ]
        )
    candidates.extend(
        [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if mono and bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
            if mono
            else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


FONT_SMALL = load_font(15)
FONT_SMALL_BOLD = load_font(15, bold=True)
FONT_BODY = load_font(18)
FONT_BODY_BOLD = load_font(18, bold=True)
FONT_TITLE = load_font(32, bold=True)
FONT_TILE = load_font(31, bold=True)
FONT_MONO = load_font(16, mono=True)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 18, fill: str = PANEL, outline: str = LINE) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def fit_title_font(draw: ImageDraw.ImageDraw, title: str) -> ImageFont.FreeTypeFont:
    for size in range(32, 21, -2):
        font = load_font(size, bold=True)
        if draw.textlength(title, font=font) <= 730:
            return font
    return load_font(20, bold=True)


def wrapped_lines(draw: ImageDraw.ImageDraw, value: Any, font: ImageFont.ImageFont, width: int, max_lines: int) -> list[str]:
    words = str(value or "—").replace("\n", " / ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > width:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
        else:
            current = candidate
    if len(lines) < max_lines and current:
        lines.append(current)
    truncated = len(lines) == max_lines and " ".join(lines) != " ".join(words)
    if truncated:
        while lines[-1] and draw.textlength(lines[-1] + "…", font=font) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines or ["—"]


def parse_puzzle_state(value: Any) -> Optional[puzzle.State]:
    numbers = [int(item) for item in re.findall(r"(?<!\d)[0-8](?!\d)", str(value or ""))]
    if len(numbers) == 9 and set(numbers) == set(range(9)):
        return tuple(numbers)
    return None


def parse_caro_board(value: Any) -> Optional[list[str]]:
    tokens = re.findall(r"(?<!\w)[XO.](?!\w)", str(value or ""))
    return tokens[-9:] if len(tokens) >= 9 else None


def draw_puzzle(draw: ImageDraw.ImageDraw, state: puzzle.State) -> None:
    rounded(draw, (34, 94, 344, 404), radius=24, fill="#e8f3f5", outline="#c8dde2")
    tile_size, gap, origin_x, origin_y = 88, 8, 53, 113
    for index, tile in enumerate(state):
        row, col = divmod(index, 3)
        x = origin_x + col * (tile_size + gap)
        y = origin_y + row * (tile_size + gap)
        box = (x, y, x + tile_size, y + tile_size)
        if tile == 0:
            draw.rounded_rectangle(box, radius=17, fill=ACCENT_SOFT, outline=ACCENT, width=2)
            label, color = "0", ACCENT_DARK
        else:
            draw.rounded_rectangle(box, radius=17, fill=PANEL, outline=LINE, width=1)
            label, color = str(tile), INK
        bounds = draw.textbbox((0, 0), label, font=FONT_TILE)
        draw.text((x + (tile_size - (bounds[2] - bounds[0])) / 2, y + 21), label, fill=color, font=FONT_TILE)


def draw_caro(draw: ImageDraw.ImageDraw, board: list[str]) -> None:
    rounded(draw, (34, 94, 344, 404), radius=24, fill="#e8f3f5", outline="#c8dde2")
    tile_size, gap, origin_x, origin_y = 88, 8, 53, 113
    for index, value in enumerate(board):
        row, col = divmod(index, 3)
        x = origin_x + col * (tile_size + gap)
        y = origin_y + row * (tile_size + gap)
        draw.rounded_rectangle((x, y, x + tile_size, y + tile_size), radius=17, fill=PANEL, outline=LINE, width=1)
        color = ACCENT_DARK if value == "X" else ROSE if value == "O" else "#94a3b8"
        bounds = draw.textbbox((0, 0), value, font=FONT_TILE)
        draw.text((x + (tile_size - (bounds[2] - bounds[0])) / 2, y + 21), value, fill=color, font=FONT_TILE)


def draw_concept(draw: ImageDraw.ImageDraw, node: Any, group: str) -> None:
    rounded(draw, (34, 94, 344, 404), radius=24, fill=PANEL, outline=LINE)
    draw.rounded_rectangle((52, 114, 326, 151), radius=12, fill=ACCENT_SOFT)
    draw.text((66, 123), group.upper(), fill=ACCENT_DARK, font=FONT_SMALL_BOLD)
    y = 176
    for line in wrapped_lines(draw, node, FONT_MONO, 250, 8):
        draw.text((58, y), line, fill=INK, font=FONT_MONO)
        y += 26


def metric_card(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: Any) -> None:
    rounded(draw, (x, y, x + 126, y + 62), radius=14, fill=PANEL, outline=LINE)
    draw.text((x + 12, y + 9), label.upper(), fill=MUTED, font=FONT_SMALL_BOLD)
    draw.text((x + 12, y + 30), str(value if value not in (None, "") else "—"), fill=INK, font=FONT_BODY_BOLD)


def selected_rows(rows: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        return rows
    indices = sorted({round(index * (len(rows) - 1) / (limit - 1)) for index in range(limit)})
    return [rows[index] for index in indices]


def frame_rows(result: puzzle.SearchResult) -> Iterable[tuple[str, dict[str, Any]]]:
    yield "Preparing real run", {"Node": puzzle.board_string(result.start), "Step": 0, "Decision/Note": "Initialize Start, Goal, frontier and reached set."}
    for row in selected_rows(result.trace_rows):
        yield "Running", row
    final_state = result.path[-1] if result.path else None
    yield "Completed" if result.found else "Stopped", {
        "Node": puzzle.board_string(final_state) if final_state else (result.trace_rows[-1].get("Node") if result.trace_rows else puzzle.board_string(result.start)),
        "Step": result.path_cost if result.path_cost is not None else result.expanded,
        "g": result.path_cost,
        "h": 0 if result.found else "—",
        "f": result.path_cost,
        "Action": result.actions[-1] if result.actions else "Finish",
        "Decision/Note": result.message,
        "Selection Key": result.termination_reason,
    }


def render_frame(algorithm: str, group: str, result: puzzle.SearchResult, phase: str, row: dict[str, Any], index: int, total: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.ellipse((650, -130, 930, 150), fill="#e2f7f4")
    draw.ellipse((-150, 320, 160, 630), fill="#eaf2ff")
    draw.text((34, 17), algorithm, fill=INK, font=fit_title_font(draw, algorithm))
    phase_width = int(draw.textlength(phase, font=FONT_SMALL_BOLD)) + 28
    draw.rounded_rectangle((34, 60, 34 + phase_width, 86), radius=13, fill=ACCENT_SOFT)
    draw.text((48, 64), phase, fill=ACCENT_DARK, font=FONT_SMALL_BOLD)
    group_text = group.replace(" Search", "")
    group_width = int(draw.textlength(group_text, font=FONT_SMALL_BOLD)) + 28
    group_x = 46 + phase_width
    draw.rounded_rectangle((group_x, 60, group_x + group_width, 86), radius=13, fill=PANEL, outline=LINE)
    draw.text((group_x + 14, 64), group_text, fill=MUTED, font=FONT_SMALL_BOLD)

    node = row.get("Node", "")
    state = parse_puzzle_state(node)
    caro = parse_caro_board(node)
    if state is not None:
        draw_puzzle(draw, state)
    elif caro is not None:
        draw_caro(draw, caro)
    else:
        draw_concept(draw, node, group)

    metric_card(draw, 375, 102, "Step", row.get("Step", index))
    metric_card(draw, 511, 102, "g / h / f", f"{row.get('g', '—')} / {row.get('h', '—')} / {row.get('f', '—')}")
    metric_card(draw, 647, 102, "Expanded", result.expanded)

    rounded(draw, (375, 178, 766, 241), radius=15, fill=PANEL, outline=LINE)
    draw.text((390, 190), "ACTION / SELECTION", fill=MUTED, font=FONT_SMALL_BOLD)
    selection = row.get("Selection Key") or row.get("Priority Rule") or row.get("Action") or "Initialize"
    for line_index, line in enumerate(wrapped_lines(draw, selection, FONT_BODY_BOLD, 350, 2)):
        draw.text((390, 213 + line_index * 23), line, fill=INK, font=FONT_BODY_BOLD)

    rounded(draw, (375, 254, 766, 381), radius=15, fill=PANEL, outline=LINE)
    draw.text((390, 268), "WHY THIS STEP", fill=ACCENT_DARK, font=FONT_SMALL_BOLD)
    note = row.get("Decision/Note") or result.message
    for line_index, line in enumerate(wrapped_lines(draw, note, FONT_BODY, 350, 4)):
        draw.text((390, 294 + line_index * 24), line, fill=INK, font=FONT_BODY)

    draw.text((36, 423), f"Actual core run  •  seed {DEMO_SEED}  •  {DEMO_HEURISTIC}  •  8-Puzzle Search Lab", fill=MUTED, font=FONT_SMALL)
    dot_x = 676
    for dot in range(total):
        color = ACCENT if dot == index else "#cbd5e1"
        draw.ellipse((dot_x + dot * 12, 423, dot_x + 7 + dot * 12, 430), fill=color)
    return image


def generate_one(algorithm: str) -> Path:
    config = puzzle.TraceConfig(
        max_expansions=4000,
        max_trace_rows=36,
        frontier_preview=4,
        reached_preview=4,
        dfs_depth_limit=35,
        ids_max_depth=24,
        ida_max_iterations=40,
        local_max_steps=50,
        random_restarts=6,
        beam_width=4,
        seed=DEMO_SEED,
        sa_max_steps=120,
    )
    result = puzzle.run_algorithm(DEMO_START, algorithm, DEMO_HEURISTIC, config)
    rows = list(frame_rows(result))
    group = puzzle.ALGORITHM_INFO[algorithm]["group"]
    frames = [render_frame(algorithm, group, result, phase, row, index, len(rows)) for index, (phase, row) in enumerate(rows)]
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
    output = algorithm_demo_path(algorithm)
    output.parent.mkdir(parents=True, exist_ok=True)
    durations = [1100] + [850] * max(0, len(frames) - 2) + [1700]
    palette_frames[0].save(
        output,
        save_all=True,
        append_images=palette_frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return output


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    created = [generate_one(algorithm) for algorithm in puzzle.DEFAULT_ALGORITHMS]
    missing = [algorithm for algorithm in puzzle.DEFAULT_ALGORITHMS if not algorithm_demo_path(algorithm).is_file()]
    if missing:
        raise SystemExit(f"Missing generated GIFs: {missing}")
    total_bytes = sum(path.stat().st_size for path in created)
    relative_dir = ASSET_DIR.relative_to(ROOT)
    print(f"Generated {len(created)} GIFs in {relative_dir.as_posix()} ({total_bytes / 1024 / 1024:.2f} MiB).")


if __name__ == "__main__":
    main()
