"""Page section renderers and HTML components for 8-Puzzle UI."""

from __future__ import annotations

import base64
import time
from html import escape
from typing import Any, Dict, Optional

import streamlit as st

import eight_puzzle_search_app as puzzle
import thu_duc_graph_coloring as thu_duc
from web.ui_text import (
    text, help_text, localize_table, localize_trace_text, localize_algorithm_group,
    ALGORITHM_BASIS, ALGORITHM_PROFILES, TABLE_COLUMNS,
)


# ---------------------------------------------------------------------------
# Cached reference data wrappers (Phase 1: @st.cache_data)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _cached_peas_model(algorithm: str, lang: str):
    return puzzle.peas_model(algorithm, lang=lang)


@st.cache_data(show_spinner=False)
def _cached_problem_model(algorithm: str, lang: str):
    return puzzle.algorithm_problem_model(algorithm, lang=lang)


@st.cache_data(show_spinner=False)
def _cached_grading_checklist(lang: str):
    return puzzle.coursework_grading_checklist(lang)


@st.cache_data(show_spinner=False)
def _cached_color_graph(max_colors: int):
    return thu_duc.color_graph(max_colors=max_colors)


def show_page_header(lang: str) -> None:
    st.markdown(
        f"""
        <div class="app-hero">
          <span class="app-kicker">{escape(text(lang, "app_kicker"))}</span>
          <h1>{escape(text(lang, "page_title"))}</h1>
          <p>{escape(text(lang, "page_subtitle"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_cards_html(result: puzzle.SearchResult, lang: str) -> str:
    labels = [
        text(lang, "path_length"),
        text(lang, "expanded_metric"),
        text(lang, "generated_metric"),
        text(lang, "runtime_metric"),
        text(lang, "memory_metric"),
    ]
    values = [
        result.path_cost if result.path_cost is not None else "N/A",
        result.expanded,
        result.generated,
        f"{result.runtime_ms:.2f} ms",
        f"{result.memory_estimate_kb:.1f} KB",
    ]
    cards = "".join(
        f'<div class="metric-card"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'
        for label, value in zip(labels, values)
    )
    return f'<div class="metric-grid">{cards}</div>'


def readiness_chip(label: str, value: str, css_class: str = "") -> str:
    class_attr = f"readiness-chip {css_class}".strip()
    return f'<div class="{class_attr}"><span>{escape(label)}</span><strong>{escape(value)}</strong></div>'


def demo_readiness_html(lang: str, algorithm: str, heuristic: str) -> str:
    run_mode = puzzle.algorithm_run_mode(algorithm, lang=lang)
    solvable = puzzle.is_solvable(st.session_state.start_state)
    preset = st.session_state.get("last_preset_name") or text(lang, "random_manual")
    mode_class = "ok" if run_mode["mode"] == "standard_solver" else "warn"
    chips = [
        readiness_chip(text(lang, "run_mode"), localize_trace_text(run_mode["label"], lang), mode_class),
        readiness_chip(text(lang, "solvable"), text(lang, "solvable") if solvable else text(lang, "unsolvable"), "ok" if solvable else "fail"),
        readiness_chip(text(lang, "current_preset"), preset, ""),
        readiness_chip(text(lang, "selected_heuristic"), heuristic, "ok"),
    ]
    description = escape(localize_trace_text(run_mode["description"], lang))
    return f'<div class="readiness-grid">{"".join(chips)}</div><p class="section-note">{description}</p>'


def trace_run_guide_html(lang: str) -> str:
    return (
        '<div class="lab-panel">'
        f'<strong>{escape(text(lang, "trace_run_title"))}</strong>'
        f'<p class="section-note">{escape(text(lang, "trace_run_steps"))}</p>'
        '</div>'
    )


def board_matrix_html(state: puzzle.State, lang: str) -> str:
    cells = []
    for index, value in enumerate(state):
        row, col = divmod(index, 3)
        tooltip = help_text(
            lang,
            "blank_tile" if value == 0 else "board_tile",
            value=value,
            row=row + 1,
            col=col + 1,
        )
        classes = "tile blank" if value == 0 else "tile"
        pos_label = f"Row {row+1}, Column {col+1}"
        cells.append(f'<div class="{classes}" role="gridcell" aria-label="{escape(pos_label)}: {value}" title="{escape(tooltip)}">{value}</div>')
    return f"""<div class="puzzle-board" role="grid" aria-label="8-Puzzle board">{''.join(cells)}</div>"""


def image_data_url(data: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def persist_game_image(uploaded_image: Any) -> bool:
    if uploaded_image is None or not hasattr(uploaded_image, "getvalue"):
        return False
    data = uploaded_image.getvalue()
    signature = f"{getattr(uploaded_image, 'name', 'image')}:{len(data)}"
    if st.session_state.get("game_image_signature") == signature and st.session_state.get("game_image_url"):
        return False
    st.session_state.game_image_url = image_data_url(data, getattr(uploaded_image, "type", "image/png") or "image/png")
    st.session_state.game_image_name = getattr(uploaded_image, "name", "image")
    st.session_state.game_image_signature = signature
    return True


def image_board_html(state: puzzle.State, image_url: str, lang: str) -> str:
    cells = []
    for index, value in enumerate(state):
        row, col = divmod(index, 3)
        if value == 0:
            label = "Ô trống 0" if lang == "vi" else "Blank tile 0"
            cells.append(f'<div class="tile blank" aria-label="{escape(label)}">0</div>')
        else:
            label = f"Ô ảnh {value}" if lang == "vi" else f"Image tile {value}"
            cells.append(
                f'<div class="tile tile-{value}" data-tile="{value}" aria-label="{escape(label)}"></div>'
            )
    return (
        f'<div class="puzzle-board image-puzzle-board" role="grid" '
        f'style="--puzzle-image: url({escape(image_url)});">{"".join(cells)}</div>'
    )


def playable_tile_grid(state: puzzle.State, lang: str) -> None:
    legal_tiles = {
        state[next_state.index(0)]
        for _action, next_state in puzzle.neighbors(state)
    }
    for row_start in range(0, 9, 3):
        cols = st.columns(3, gap="small")
        for offset, col in enumerate(cols):
            index = row_start + offset
            tile = state[index]
            movable = tile != 0 and tile in legal_tiles
            label = "0" if tile == 0 else str(tile)
            help_label = (
                ("Bấm để di chuyển" if lang == "vi" else "Click to move")
                if movable
                else ("Ô này chưa đi được" if lang == "vi" else "This tile is not movable")
            )
            with col:
                if st.button(label, key=f"play_tile_{index}_{tile}_{st.session_state.game_moves}", disabled=not movable, help=help_label, width="stretch"):
                    move_tile_in_game(tile)
                    st.rerun()
    note = "Bấm trực tiếp ô hợp lệ cạnh ô trống để di chuyển." if lang == "vi" else "Click a legal tile next to the blank to move it."
    st.info(note)


# Shared Thu Duc color mapping: VN palette name → (English key, hex color)
_THU_DUC_COLORS: dict[str, tuple[str, str]] = {
    "Xanh ngoc": ("thu_duc_color_teal", "#0f766e"),
    "Vang dat": ("thu_duc_color_amber", "#b7791f"),
    "Do gach": ("thu_duc_color_brick", "#b42318"),
    "Tim than": ("thu_duc_color_violet", "#4c1d95"),
    "Xanh troi": ("thu_duc_color_sky", "#0369a1"),
    "Hong sen": ("thu_duc_color_lotus", "#be185d"),
}

# Internal English key → hex (used by thu_duc_map_svg for SVG fill lookup)
_THU_DUC_COLOR_HEX: dict[str, str] = {
    en_key: hex_val for _vn, (en_key, hex_val) in _THU_DUC_COLORS.items()
}


def thu_duc_map_svg(result: thu_duc.ColoringResult, lang: str) -> str:
    def _resolve_color(vn_name: str) -> str:
        en_key = _THU_DUC_COLORS.get(vn_name, ("", "#94a3b8"))[0]
        return _THU_DUC_COLOR_HEX.get(en_key, "#94a3b8")
    edges = []
    for left, right in thu_duc.EDGES:
        x1, y1 = thu_duc.WARD_POSITIONS[left]
        x2, y2 = thu_duc.WARD_POSITIONS[right]
        edges.append(
            f'<line x1="{x1 * 100:.1f}" y1="{y1 * 100:.1f}" x2="{x2 * 100:.1f}" y2="{y2 * 100:.1f}" />'
        )
    nodes = []
    for ward, (x, y) in thu_duc.WARD_POSITIONS.items():
        color = _resolve_color(result.assignments.get(ward, ""))
        nodes.append(
            f'<g><circle cx="{x * 100:.1f}" cy="{y * 100:.1f}" r="4.4" fill="{color}" />'
            f'<text x="{x * 100:.1f}" y="{y * 100 + 8:.1f}">{escape(ward)}</text></g>'
        )
    return (
        '<div class="lab-panel">'
        f'<svg viewBox="0 0 100 108" role="img" aria-label="{escape(text(lang, "thu_duc_title"))}" '
        'style="width:100%;max-height:620px;">'
        '<style>line{stroke:var(--map-edge);stroke-width:.7} circle{stroke:var(--map-node-stroke);stroke-width:.7}'
        'text{font-size:2.35px;fill:var(--ink);text-anchor:middle;font-weight:700}</style>'
        f'{"".join(edges)}{"".join(nodes)}</svg></div>'
    )


def _translate_color_name(vn_name: str, lang: str) -> str:
    """Translate a Vietnamese palette color name to the current display language."""
    entry = _THU_DUC_COLORS.get(vn_name)
    if entry is None:
        return vn_name
    return text(lang, entry[0])


def _localize_coloring_rows(rows: list[dict], lang: str) -> list[dict]:
    """Translate Vietnamese color names in coloring table rows."""
    localized = []
    for row in rows:
        r = dict(row)
        r["Color"] = _translate_color_name(r.get("Color", ""), lang)
        localized.append(r)
    return localized


def _localize_coloring_steps(steps: list[dict], lang: str) -> list[dict]:
    """Translate Vietnamese color names in coloring step rows."""
    localized = []
    for step in steps:
        s = dict(step)
        s["Chosen color"] = _translate_color_name(s.get("Chosen color", ""), lang)
        blocked_raw = s.get("Blocked colors", "")
        if blocked_raw and blocked_raw != "-":
            translated = [_translate_color_name(c.strip(), lang) for c in blocked_raw.split(",")]
            s["Blocked colors"] = ", ".join(translated)
        localized.append(s)
    return localized


def _build_palette_legend_html(result, lang: str) -> str:
    """Build an HTML legend showing which colors map to which names."""
    items = []
    for vn_name in result.colors_used:
        display_name = _translate_color_name(vn_name, lang)
        hex_color = _THU_DUC_COLORS.get(vn_name, ("", "#94a3b8"))[1]
        items.append(
            f'<span style="display:inline-flex;align-items:center;gap:6px;margin-right:14px;">'
            f'<span style="width:14px;height:14px;border-radius:3px;background:{hex_color};display:inline-block;"></span>'
            f'{escape(display_name)}</span>'
        )
    if not items:
        return ""
    return f'<div class="lab-panel" style="margin:0.5rem 0 1rem;"><strong>{"Palette" if lang == "en" else "Bảng màu"}:</strong> {"".join(items)}</div>'


def show_thu_duc_graph_coloring_page(lang: str) -> None:
    st.markdown(
        f"""
        <div class="lab-panel">
          <strong>{escape(text(lang, "thu_duc_title"))}</strong>
          <p class="section-note">{escape(text(lang, "thu_duc_subtitle"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    max_colors = st.slider(text(lang, "thu_duc_palette"), 3, len(thu_duc.PALETTE), 4, key="thu_duc_max_colors")
    result = _cached_color_graph(max_colors)
    status = text(lang, "thu_duc_valid") if result.valid else text(lang, "thu_duc_invalid")
    cards = "".join(
        f'<div class="metric-card"><span>{escape(label)}</span><strong>{value}</strong></div>'
        for label, value in [
            (text(lang, "thu_duc_stat_regions"), len(thu_duc.REGIONS)),
            (text(lang, "thu_duc_stat_edges"), len(thu_duc.EDGES)),
            (text(lang, "thu_duc_stat_colors_used"), len(result.colors_used)),
            (text(lang, "thu_duc_stat_status"), status),
        ]
    )
    st.markdown(f'<h3>{escape(text(lang, "thu_duc_stats"))}</h3><div class="metric-grid">{cards}</div>', unsafe_allow_html=True)

    # Palette color legend (color swatches with bilingual names)
    legend_html = _build_palette_legend_html(result, lang)
    if legend_html:
        st.markdown(legend_html, unsafe_allow_html=True)

    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown(thu_duc_map_svg(result, lang), unsafe_allow_html=True)
    with right:
        # Validation result banner
        if result.conflicts:
            conflict_list = " / ".join(
                f"{escape(left)} - {escape(right)}" for left, right in result.conflicts
            )
            if lang == "vi":
                st.error(f"Phát hiện {len(result.conflicts)} cặp xung đột: {conflict_list}")
            else:
                st.error(f"Found {len(result.conflicts)} conflicting pair(s): {conflict_list}")
        else:
            st.success(text(lang, "thu_duc_no_conflicts"))
        st.subheader(text(lang, "thu_duc_assignments"))
        st.dataframe(_localize_coloring_rows(thu_duc.coloring_rows(result), lang), width="stretch", hide_index=True)
    st.subheader(text(lang, "thu_duc_steps"))
    st.dataframe(_localize_coloring_steps(result.steps, lang), width="stretch", hide_index=True)


def show_image_puzzle_page(lang: str) -> None:
    st.markdown(
        f"""
        <div class="app-hero">
          <span class="app-kicker">8-Puzzle / Image Game</span>
          <h1>{escape(text(lang, "image_game_title"))}</h1>
          <p>{escape(text(lang, "image_game_note"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="panel-heading">
              <h2>{escape(text(lang, "image_controls"))}</h2>
              <span>{escape(text(lang, "game_title"))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_image = st.file_uploader(
            text(lang, "image_upload"),
            type=["png", "jpg", "jpeg", "webp"],
            key="game_image_page_uploader",
        )
        if uploaded_image is not None and persist_game_image(uploaded_image):
            st.rerun()
        mode_text = text(lang, "image_mode_on") if st.session_state.game_image_url else text(lang, "image_mode_off")
        st.caption(mode_text)
        if st.session_state.game_image_url:
            st.success(text(lang, "image_ready"))
            if st.button(text(lang, "clear_image"), key="game_clear_image_page", width="stretch"):
                st.session_state.game_image_url = ""
                st.session_state.game_image_name = ""
                st.session_state.game_image_signature = ""
                st.rerun()
        else:
            st.info(text(lang, "image_game_note"))
            
        st.divider()
        try:
            import sidebar_game
            theme_vars = {
                "--background-color": st.get_option("theme.backgroundColor") or "#f7f5f2",
                "--secondary-background-color": st.get_option("theme.secondaryBackgroundColor") or "#faf8f5",
                "--text-color": st.get_option("theme.textColor") or "#1e1b18",
                "--primary-color": st.get_option("theme.primaryColor") or "#0d9488",
            }
            st.components.v1.html(sidebar_game.get_sidebar_game_html("sidebar_puzzle.png", theme_vars), height=800)
        except ImportError:
            st.warning("Interactive image game unavailable. The sidebar_puzzle.png asset may be missing. Switch to number mode or upload a custom image." if lang == "en" else "Trò chơi xếp hình tương tác không khả dụng. Có thể thiếu file sidebar_puzzle.png. Thử chuyển sang chế độ số hoặc tải ảnh khác.")
        except Exception as e:
            st.error(f"{'Failed to load image puzzle game' if lang == 'en' else 'Không thể tải trò chơi xếp hình ảnh'}: {e}. {'Try refreshing the page or clearing the uploaded image.' if lang == 'en' else 'Thử làm mới trang hoặc xóa ảnh đã tải.'}")
            
        show_goal_panel(lang)


def mini_board_html(state: puzzle.State) -> str:
    cells = []
    for idx, value in enumerate(state):
        classes = "mini-tile mini-blank" if value == 0 else "mini-tile"
        row_label = f"Row {idx//3 + 1}, Col {idx%3 + 1}"
        cells.append(f'<div class="{classes}" role="gridcell" aria-label="{row_label}: {value}">{value}</div>')
    return f'<div class="mini-board" role="grid" aria-label="Mini board">{"".join(cells)}</div>'


def trace_states_from_text(value: Any, limit: int = 4) -> list[puzzle.State]:
    text_value = str(value or "").strip()
    if not text_value:
        return []
    states: list[puzzle.State] = []
    for chunk in text_value.split("---"):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            states.append(puzzle.parse_state(chunk))
        except ValueError:
            continue
        if len(states) >= limit:
            break
    return states


def trace_state_panel_html(title: str, subtitle: str, states: list[puzzle.State], fallback: Any) -> str:
    if states:
        cards = "".join(
            f'<div class="state-card"><div class="state-card-title">#{idx + 1}</div>{mini_board_html(state)}</div>'
            for idx, state in enumerate(states)
        )
    else:
        cards = f'<div class="trace-detail"><pre>{escape(str(fallback) if fallback not in (None, "") else "-")}</pre></div>'
    return (
        '<div class="trace-state-panel">'
        f'<h4>{escape(title)}</h4>'
        f'<p>{escape(subtitle)}</p>'
        f'<div class="state-card-grid">{cards}</div>'
        '</div>'
    )


def show_board(title: str, state: puzzle.State, lang: str, help_key: str | None = None) -> None:
    if title:
        tooltip = f' title="{escape(help_text(lang, help_key))}"' if help_key else ""
        st.markdown(f"<strong{tooltip}>{escape(title)}</strong>", unsafe_allow_html=True)
    st.markdown(board_matrix_html(state, lang), unsafe_allow_html=True)


def show_goal_panel(lang: str) -> None:
    st.markdown(
        f"<strong title=\"{escape(help_text(lang, 'goal_board'))}\">{escape(text(lang, 'goal_state'))}</strong>",
        unsafe_allow_html=True,
    )
    st.caption(text(lang, "goal_caption"))
    st.markdown(board_matrix_html(puzzle.GOAL_STATE, lang), unsafe_allow_html=True)


def heuristic_formula(lang: str, heuristic: str) -> str:
    if heuristic == "manhattan":
        if lang == "vi":
            return (
                "Manhattan:  "
                r"$h(s)=\sum_{t=1}^{8}(|row_s(t)-row_g(t)|+|col_s(t)-col_g(t)|)$"
            )
        return (
            "Manhattan distance:  "
            r"$h(s)=\sum_{t=1}^{8}(|row_s(t)-row_g(t)|+|col_s(t)-col_g(t)|)$"
        )
    if heuristic == "linear_conflict":
        if lang == "vi":
            return (
                "Linear Conflict:  "
                r"$h(s)=h_{Manhattan}(s)+2\times conflicts(s)$; "
                "vẫn admissible và thường informed hơn Manhattan."
            )
        return (
            "Linear Conflict:  "
            r"$h(s)=h_{Manhattan}(s)+2\times conflicts(s)$; "
            "still admissible and usually more informed than Manhattan."
        )
    if lang == "vi":
        return "Misplaced tiles:  " r"$h(s)=|\{t \in \{1..8\}: position_s(t) \ne position_g(t)\}|$"
    return "Misplaced tiles:  " r"$h(s)=|\{t \in \{1..8\}: position_s(t) \ne position_g(t)\}|$"


def academic_problem_markdown(lang: str, heuristic: str) -> str:
    if lang == "vi":
        return f"""
**{text(lang, "objective")}.** Tìm chuỗi hành động ngắn hoặc tốt nhất biến trạng thái bắt đầu `s0`
thành trạng thái đích `sg = (1,2,3,4,5,6,7,8,0)`.

**{text(lang, "state_space")}.** Mỗi trạng thái là một hoán vị của 9 ô `(0..8)`;
ô `0` biểu diễn ô trống. Trạng thái chỉ được xét nếu parity inversion tương thích với goal.

**{text(lang, "transition_model")}.** Tập hành động `A(s) = {{Up, Down, Left, Right}}`
gồm các phép di chuyển hợp lệ của ô trống. Trong bài này chi phí mỗi bước là `c(s,a,s') = 1`,
vì vậy `g(n)` chính là số bước từ start đến node `n`.

**{text(lang, "heuristic_formula")}.** {heuristic_formula(lang, heuristic)}
"""
    return f"""
**{text(lang, "objective")}.** Find a shortest or best action sequence that transforms the start state `s0`
into the goal state `sg = (1,2,3,4,5,6,7,8,0)`.

**{text(lang, "state_space")}.** Each state is a permutation of the 9 tiles `(0..8)`;
tile `0` denotes the blank. A state is searched only when its inversion parity is compatible with the goal.

**{text(lang, "transition_model")}.** The action set `A(s) = {{Up, Down, Left, Right}}`
contains all legal blank-tile moves. In this app every step has cost `c(s,a,s') = 1`,
so `g(n)` is the number of moves from the start node to node `n`.

**{text(lang, "heuristic_formula")}.** {heuristic_formula(lang, heuristic)}
"""


def evaluation_rows(lang: str) -> Any:
    if lang == "vi":
        rows = [
            {"Criterion": "Complete", "Academic meaning": "Thuật toán có đảm bảo tìm nghiệm nếu nghiệm tồn tại hay không."},
            {"Criterion": "Optimal", "Academic meaning": "Thuật toán có đảm bảo trả về nghiệm có chi phí nhỏ nhất hay không."},
            {"Criterion": "Expanded", "Academic meaning": "Số node đã được lấy ra để kiểm tra và sinh successor."},
            {"Criterion": "Generated", "Academic meaning": "Số node successor đã được tạo trong quá trình tìm kiếm."},
            {"Criterion": "Max Frontier", "Academic meaning": "Kích thước frontier lớn nhất, phản ánh áp lực bộ nhớ."},
            {"Criterion": "Runtime ms", "Academic meaning": "Thời gian thực nghiệm trên cấu hình hiện tại."},
        ]
    else:
        rows = [
            {"Criterion": "Complete", "Academic meaning": "Whether the algorithm is guaranteed to find a solution if one exists."},
            {"Criterion": "Optimal", "Academic meaning": "Whether the returned solution is guaranteed to have minimum path cost."},
            {"Criterion": "Expanded", "Academic meaning": "Number of nodes removed for testing and successor generation."},
            {"Criterion": "Generated", "Academic meaning": "Number of successor nodes produced during search."},
            {"Criterion": "Max Frontier", "Academic meaning": "Largest frontier size, used as a memory-pressure proxy."},
            {"Criterion": "Runtime ms", "Academic meaning": "Empirical runtime under the current configuration."},
        ]
    return localize_table(puzzle._to_table(rows), lang)


def trace_glossary_rows(lang: str) -> Any:
    if lang == "vi":
        rows = [
            {"Trace column": "Node", "Definition": "Trạng thái đang được chọn để xét ở vòng lặp hiện tại."},
            {"Trace column": "Frontier", "Definition": "Tập biên: các node đã sinh nhưng chưa mở rộng."},
            {"Trace column": "Reached", "Definition": "Các trạng thái đã được ghi nhận để tránh lặp hoặc so sánh chi phí tốt hơn."},
            {"Trace column": "g", "Definition": "Chi phí đường đi từ start đến node hiện tại."},
            {"Trace column": "h", "Definition": "Ước lượng chi phí còn lại từ node hiện tại đến goal."},
            {"Trace column": "f", "Definition": "Hàm đánh giá dùng để ưu tiên node, ví dụ A*: f=g+h."},
            {"Trace column": "Priority Rule", "Definition": "Quy tắc học thuật mà thuật toán dùng để chọn node tiếp theo."},
            {"Trace column": "Selection Key", "Definition": "Giá trị cụ thể tại vòng lặp hiện tại, ví dụ g, h, f, threshold hoặc temperature."},
            {"Trace column": "Generated Children", "Definition": "Số successor hợp lệ được sinh ra từ node/current state trong vòng lặp."},
            {"Trace column": "Skipped States", "Definition": "Số state bị bỏ qua do đã reached, nằm trên path hiện tại, hoặc bị giới hạn depth."},
        ]
    else:
        rows = [
            {"Trace column": "Node", "Definition": "The state selected for examination in the current iteration."},
            {"Trace column": "Frontier", "Definition": "The boundary set: generated nodes not yet expanded."},
            {"Trace column": "Reached", "Definition": "States recorded to prevent repetition or compare better path costs."},
            {"Trace column": "g", "Definition": "Path cost from the start state to the current node."},
            {"Trace column": "h", "Definition": "Estimated remaining cost from the current node to the goal."},
            {"Trace column": "f", "Definition": "Priority/evaluation value, for example A*: f=g+h."},
            {"Trace column": "Priority Rule", "Definition": "The academic rule the algorithm uses to select the next node."},
            {"Trace column": "Selection Key", "Definition": "The concrete value for this iteration, such as g, h, f, threshold, or temperature."},
            {"Trace column": "Generated Children", "Definition": "Number of valid successors generated from the node/current state."},
            {"Trace column": "Skipped States", "Definition": "States skipped because they were reached, on the current path, or blocked by depth limits."},
        ]
    return localize_table(puzzle._to_table(rows), lang)


def status_label(lang: str, status: str) -> str:
    if status == "yes":
        return text(lang, "yes")
    if status == "no":
        return text(lang, "no")
    return text(lang, "implicit")


def fallback_priority_basis(lang: str, algorithm: str) -> Dict[str, Any]:
    info = puzzle.ALGORITHM_INFO[algorithm]
    group = info["group"]
    rule = puzzle.PRIORITY_RULES.get(algorithm, "")
    if group == "Uninformed Search":
        primary = "g(n)/depth" if lang == "en" else "g(n)/độ sâu"
        g_status, h_status, f_status = "implicit", "no", "no"
    elif group == "Informed Search":
        primary = "h(n) or f(n)=g(n)+h(n)"
        g_status, h_status, f_status = "implicit", "yes", "implicit"
    elif group == "Local Search":
        primary = "h(n)"
        g_status, h_status, f_status = "no", "yes", "no"
    elif group == "Complex Environments":
        primary = "belief/conditional/online state estimate" if lang == "en" else "belief state / quan sát một phần / ước lượng online"
        g_status, h_status, f_status = "implicit", "yes", "implicit"
    elif group == "Constraint Satisfaction Problems":
        primary = "constraints/conflicts/horizon" if lang == "en" else "ràng buộc / xung đột / planning horizon"
        g_status, h_status, f_status = "implicit", "implicit", "no"
    else:
        primary = "utility / expected value" if lang == "en" else "utility / giá trị kỳ vọng"
        g_status, h_status, f_status = "no", "implicit", "no"
    if lang == "vi":
        meaning = {
            "Uninformed Search": "Chi phí/độ sâu chỉ dùng khi đường đi có ý nghĩa; h(n) không quyết định thứ tự mở node.",
            "Informed Search": "Heuristic là tri thức định hướng; A*/IDA* kết hợp thêm g(n) để giữ tối ưu.",
            "Local Search": "h(n) đo chất lượng trạng thái hiện tại; thuật toán không duy trì đường đi tối ưu toàn cục.",
            "Complex Environments": "h(n) chỉ là ước lượng chất lượng trong belief/online/partial model, không biến mô hình này thành solver chuẩn.",
            "Constraint Satisfaction Problems": "Trọng tâm là biến, miền và ràng buộc; h(n) chỉ hỗ trợ đo xung đột/trạng thái khi cần.",
            "Adversarial / Stochastic Search": "Trọng tâm là utility, đối thủ hoặc chance node trong Caro; h(n) không quyết định nước Caro.",
        }.get(group, "Thành phần này phụ thuộc mô hình học thuật của thuật toán.")
    else:
        meaning = "Path cost/depth is tracked when a path is meaningful."
    return {
        "primary": primary,
        "rule": rule,
        "g": (g_status, meaning),
        "h": (h_status, "Heuristic là ước lượng chất lượng/khoảng cách khi mô hình cần." if lang == "vi" else "Heuristic is used when the educational model needs a state-quality estimate."),
        "f": (f_status, "f(n)=g(n)+h(n) chỉ là priority chính của A*/IDA*." if lang == "vi" else "Combined f(n) is used only by A*/IDA* style algorithms."),
    }


def fallback_algorithm_profile(lang: str, algorithm: str) -> Dict[str, str]:
    info = puzzle.ALGORITHM_INFO[algorithm]
    group = info["group"]
    suitable = info.get("suitable", "")
    if lang == "vi":
        group_notes = {
            "Complex Environments": "Mô hình môi trường mở rộng: belief state, quan sát một phần, online update hoặc nondeterministic outcome.",
            "Constraint Satisfaction Problems": "Mô hình hóa bài toán bằng biến, miền giá trị và ràng buộc theo planning horizon.",
            "Adversarial / Stochastic Search": "Dùng Caro mini-game để minh họa Minimax, Alpha-Beta và Expectimax vì 8-puzzle không có đối thủ.",
        }
        return {
            "Family": group,
            "Selection rule": puzzle.PRIORITY_RULES.get(algorithm, ""),
            "Evaluation function": "Xem `Selection Key` và `Decision/Note` trong trace.",
            "Guarantee": f"Complete: {info['complete']}. Optimal: {info['optimal']}.",
            "Main limitation": group_notes.get(group, suitable),
            "pseudo": (
                "khởi tạo mô hình học thuật từ ma trận hiện tại\n"
                "for mỗi bước trong giới hạn:\n"
                "    chọn/cập nhật theo quy tắc của thuật toán\n"
                "    ghi Node / Frontier / Reached / Decision vào trace\n"
                "trả SearchResult kèm ghi chú giới hạn mô hình"
            ),
        }
    return {
        "Family": group,
        "Selection rule": puzzle.PRIORITY_RULES.get(algorithm, ""),
        "Evaluation function": "See trace Selection Key and Decision/Note",
        "Guarantee": f"Complete: {info['complete']}. Optimal: {info['optimal']}.",
        "Main limitation": suitable,
        "pseudo": (
            "initialize educational model from current board\n"
            "for each bounded step:\n"
            "    choose/update according to the algorithm rule\n"
            "    emit Node / Frontier / Reached / Decision trace\n"
            "return SearchResult with explicit limitation note"
        ),
    }


def priority_basis_rows(lang: str, algorithm: str) -> Any:
    basis = ALGORITHM_BASIS.get(lang, {}).get(algorithm) or fallback_priority_basis(lang, algorithm)
    rows = []
    for component in ["g", "h", "f"]:
        status, meaning = basis[component]
        rows.append(
            {
                "Component": f"{component}(n)",
                text(lang, "uses_component"): status_label(lang, status),
                text(lang, "component_meaning"): meaning,
            }
        )
    return puzzle._to_table(rows)


def show_priority_basis(lang: str, algorithm: str) -> None:
    basis = ALGORITHM_BASIS.get(lang, {}).get(algorithm) or fallback_priority_basis(lang, algorithm)
    st.markdown(f"**{text(lang, 'primary_basis')}:** `{basis['primary']}`")
    st.markdown(f"**{text(lang, 'priority_rule')}:** {basis['rule']}")
    st.dataframe(priority_basis_rows(lang, algorithm), width="stretch", hide_index=True)


def show_algorithm_profile(lang: str, algorithm: str) -> None:
    profile = ALGORITHM_PROFILES.get(lang, {}).get(algorithm) or fallback_algorithm_profile(lang, algorithm)
    st.markdown(f"#### {text(lang, 'priority_basis')}")
    show_priority_basis(lang, algorithm)
    st.markdown(
        f"""
**{TABLE_COLUMNS[lang].get("Family", "Family")}:** {profile["Family"]}

**{TABLE_COLUMNS[lang].get("Selection rule", "Selection rule")}:** {profile["Selection rule"]}

**{TABLE_COLUMNS[lang].get("Evaluation function", "Evaluation function")}:** `{profile["Evaluation function"]}`

**{TABLE_COLUMNS[lang].get("Guarantee", "Guarantee")}:** {profile["Guarantee"]}

**{TABLE_COLUMNS[lang].get("Main limitation", "Main limitation")}:** {profile["Main limitation"]}
"""
    )
    st.code(profile["pseudo"], language="text")


def heuristic_usage_note(lang: str, algorithm: str) -> str:
    group = puzzle.ALGORITHM_INFO[algorithm]["group"]
    priority_algorithms = {
        "Greedy",
        "A*",
        "IDA*",
        "Simple Hill Climbing",
        "Steepest-Ascent Hill Climbing",
        "Stochastic Hill Climbing",
        "Random-Restart Hill Climbing",
        "Local Beam Search",
        "Simulated Annealing",
    }
    if algorithm in {"BFS", "DFS", "UCS", "IDS"}:
        return text(lang, "heuristic_note_uninformed")
    if algorithm in priority_algorithms:
        return text(lang, "heuristic_note_informed")
    if group == "Constraint Satisfaction Problems":
        return text(lang, "heuristic_note_csp")
    if group == "Adversarial / Stochastic Search":
        return text(lang, "heuristic_note_adversarial")
    return text(lang, "heuristic_note_complex")


def show_grading_checklist(lang: str) -> None:
    st.subheader(text(lang, "grading_checklist"))
    st.dataframe(
        localize_table(puzzle._to_table(_cached_grading_checklist(lang)), lang),
        width="stretch",
        hide_index=True,
    )


def show_peas_model(lang: str, algorithm: str) -> None:
    rows = _cached_peas_model(algorithm, lang)
    for row in rows:
        st.markdown(
            f"""
            <div class="lab-panel">
              <strong>{escape(row["PEAS"])}</strong><br>
              <span class="section-note">{escape(row["Definition"])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_problem_variant(lang: str, algorithm: str) -> None:
    rows = _cached_problem_model(algorithm, lang)
    key_name = "Mục" if lang == "vi" else "Item"
    definition_name = "Định nghĩa" if lang == "vi" else "Definition"
    for row in rows:
        st.markdown(
            f"""
            <div class="lab-panel">
              <strong>{escape(row[key_name])}</strong>
              <pre style="white-space: pre-wrap; margin: 0.45rem 0 0; background: transparent; border: 0; padding: 0; color: var(--muted); font: inherit;">{escape(row[definition_name])}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )


def current_partial_goal_pattern() -> Any:
    text_value = st.session_state.get("partial_goal_pattern_text", "1 2 ? ? ? ? ? ? ?")
    try:
        return puzzle.parse_partial_goal(text_value)
    except ValueError:
        return puzzle.PARTIAL_GOAL_PATTERN


def partial_goal_controls(lang: str, algorithm: str) -> None:
    if algorithm != "Partially Observable Search":
        return
    label = "Partial goal pattern" if lang == "en" else "Goal biết một phần"
    help_text_value = (
        "Use 9 entries. Digits 0..8 are known cells, ? means unknown. Example: 1 2 ? ? ? ? ? ? ?."
        if lang == "en"
        else "Nhập 9 ô. Số 0..8 là ô biết trước, ? là ô chưa biết. Ví dụ: 1 2 ? ? ? ? ? ? ?."
    )
    st.text_input(label, key="partial_goal_pattern_text", help=help_text_value)
    try:
        pattern = puzzle.parse_partial_goal(st.session_state.partial_goal_pattern_text)
        st.caption(puzzle.partial_goal_string(pattern).replace("\n", " / "))
    except ValueError as exc:
        st.error(f"{'Invalid partial goal pattern' if lang == 'en' else 'Goal một phần không hợp lệ'}: {exc}. {'Use numbers 0-8 and ? for unknown cells. Example: 1 2 ? ? ? ? ? ? ?' if lang == 'en' else 'Dùng số 0-8 và ? cho ô chưa biết. Ví dụ: 1 2 ? ? ? ? ? ? ?'}")
    button_label = "Random partial goal" if lang == "en" else "Random Goal một phần"
    if st.button(button_label, width="stretch", key="random_partial_goal"):
        pattern = puzzle.random_partial_goal_pattern(seed=st.session_state.seed + st.session_state.shuffle_count, reveal_count=2)
        st.session_state.partial_goal_pattern_text = " ".join("?" if value is None else str(value) for value in pattern)
        st.rerun()


def show_academic_context(lang: str, algorithm: str, heuristic: str) -> None:
    st.subheader(text(lang, "academic_panel"))
    with st.expander(text(lang, "grading_checklist"), expanded=False):
        show_grading_checklist(lang)
    with st.expander(text(lang, "peas_model"), expanded=False):
        show_peas_model(lang, algorithm)
    with st.expander(text(lang, "problem_variant"), expanded=False):
        show_problem_variant(lang, algorithm)
    with st.expander(text(lang, "problem_definition"), expanded=False):
        st.markdown(academic_problem_markdown(lang, heuristic))
    with st.expander(text(lang, "algorithm_profile"), expanded=False):
        show_algorithm_profile(lang, algorithm)
    with st.expander(text(lang, "evaluation_criteria"), expanded=False):
        st.dataframe(evaluation_rows(lang), width="stretch", hide_index=True)
    with st.expander(text(lang, "trace_glossary"), expanded=False):
        st.dataframe(trace_glossary_rows(lang), width="stretch", hide_index=True)


def route_rows(result: puzzle.SearchResult, lang: str, heuristic: str) -> Any:
    rows = []
    h_func = puzzle.get_heuristic(heuristic)
    for index, state in enumerate(result.path):
        action = text(lang, "start") if index == 0 else localize_action(result.actions[index - 1], lang)
        rows.append(
            {
                "Step": index,
                "Action": action,
                "g": index,
                "h": h_func(state),
                "f": index + h_func(state),
                "State": puzzle.board_string(state),
            }
        )
    return localize_table(puzzle._to_table(rows), lang)


def localized_action_sequence(result: puzzle.SearchResult, lang: str) -> str:
    if not result.actions:
        return text(lang, "start")
    return " -> ".join(localize_action(action, lang) for action in result.actions)


def show_path_player(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    st.subheader(text(lang, "path_player"))
    if not result.path:
        st.info(text(lang, "no_solution_path"))
        return

    max_step = len(result.path) - 1
    st.session_state.playback_step = min(st.session_state.playback_step, max_step)
    current_step = st.session_state.playback_step

    prev_col, slider_col, next_col = st.columns([1, 3, 1])
    with prev_col:
        if st.button(text(lang, "previous_step"), disabled=current_step <= 0, width="stretch", help=help_text(lang, "previous_step")):
            st.session_state.playback_step = max(0, current_step - 1)
            st.rerun()
    with slider_col:
        selected_step = st.slider(
            text(lang, "step_slider"),
            min_value=0,
            max_value=max_step,
            value=current_step,
            help=help_text(lang, "step_slider"),
        )
        if selected_step != current_step:
            st.session_state.playback_step = selected_step
            current_step = selected_step
    with next_col:
        if st.button(text(lang, "next_step"), disabled=current_step >= max_step, width="stretch", help=help_text(lang, "next_step")):
            st.session_state.playback_step = min(max_step, current_step + 1)
            st.rerun()

    current_state = result.path[current_step]
    previous_state = result.path[current_step - 1] if current_step > 0 else result.path[0]
    current_action = text(lang, "start") if current_step == 0 else localize_action(result.actions[current_step - 1], lang)
    next_action = (
        localize_action(result.actions[current_step], lang)
        if current_step < len(result.actions)
        else "-"
    )
    h_func = puzzle.get_heuristic(heuristic)
    h_value = h_func(current_state)

    metric_cols = st.columns(5)
    metric_cols[0].metric(text(lang, "step"), f"{current_step}/{max_step}", help=help_text(lang, "metric_step"))
    metric_cols[1].metric("g(n)", current_step, help=help_text(lang, "metric_g"))
    metric_cols[2].metric("h(n)", h_value, help=help_text(lang, "metric_h"))
    metric_cols[3].metric("f(n)", current_step + h_value, help=help_text(lang, "metric_f"))
    metric_cols[4].metric(text(lang, "total_steps"), max_step, help=help_text(lang, "metric_total_steps"))

    st.caption(f"{text(lang, 'current_action')}: {current_action} | {text(lang, 'next_action')}: {next_action}")
    before_col, after_col = st.columns(2)
    with before_col:
        show_board(text(lang, "before_move"), previous_state, lang)
    with after_col:
        show_board(text(lang, "after_move"), current_state, lang)

    st.markdown(f"**{text(lang, 'route_sequence')}:** `{localized_action_sequence(result, lang)}`")
    with st.expander(text(lang, "route_table"), expanded=False):
        st.dataframe(route_rows(result, lang, heuristic), width="stretch", hide_index=True)


def certificate_rows(validation: Dict[str, Any], lang: str) -> Any:
    labels = {
        "path_valid": "Path hợp lệ" if lang == "vi" else "Valid path",
        "cost_matches_actions": "Cost khớp action" if lang == "vi" else "Cost matches actions",
        "terminal_matches_goal": "Terminal khớp Goal" if lang == "vi" else "Terminal matches goal",
        "solvability_checked": "Đã kiểm tra solvability" if lang == "vi" else "Solvability checked",
        "heuristic_values_valid": "Heuristic hợp lệ" if lang == "vi" else "Valid heuristic values",
        "error": "Lỗi" if lang == "vi" else "Error",
    }
    rows = []
    for key in ["path_valid", "cost_matches_actions", "terminal_matches_goal", "solvability_checked", "heuristic_values_valid"]:
        value = validation.get(key)
        rows.append({"Check": labels[key], "Value": "PASS" if value else "FAIL"})
    rows.append({"Check": labels["error"], "Value": validation.get("error") or "-"})
    return localize_table(puzzle._to_table(rows), lang)


def certificate_chips_html(validation: Dict[str, Any], lang: str) -> str:
    labels = {
        "path_valid": "Path hợp lệ" if lang == "vi" else "Valid path",
        "cost_matches_actions": "Cost khớp action" if lang == "vi" else "Cost matches actions",
        "terminal_matches_goal": "Terminal khớp Goal" if lang == "vi" else "Terminal matches goal",
        "solvability_checked": "Đã kiểm tra solvability" if lang == "vi" else "Solvability checked",
        "heuristic_values_valid": "Heuristic hợp lệ" if lang == "vi" else "Valid heuristic values",
    }
    cards = []
    for key, label in labels.items():
        passed = bool(validation.get(key))
        status = text(lang, "certificate_pass") if passed else text(lang, "certificate_fail")
        css_class = "pass" if passed else "fail"
        cards.append(
            f'<div class="status-chip {css_class}"><span>{escape(label)}</span><strong>{escape(status)}</strong></div>'
        )
    return f'<div class="status-grid">{"".join(cards)}</div>'


def show_certificate(result: puzzle.SearchResult, lang: str, heuristic: str) -> Dict[str, Any]:
    validation = puzzle.validate_result(result, heuristic)
    st.subheader(text(lang, "algorithm_certificate"))
    st.markdown(certificate_chips_html(validation, lang), unsafe_allow_html=True)
    st.dataframe(certificate_rows(validation, lang), width="stretch", hide_index=True)
    return validation


def show_trace_story(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    st.subheader(text(lang, "trace_story"))
    story_rows = puzzle.build_trace_story(result, heuristic)
    if not story_rows:
        st.info("Trace story is empty because trace capture is disabled." if lang == "en" else "Phần giải thích trace đang trống vì trace đang bị tắt.")
        return
    st.dataframe(localize_table(puzzle._to_table(story_rows[:20]), lang), width="stretch", hide_index=True)


def trace_detail_card(label: str, value: Any) -> str:
    return (
        '<div class="trace-detail">'
        f"<span>{escape(str(label))}</span>"
        f"<pre>{escape(str(value) if value not in (None, '') else '-')}</pre>"
        "</div>"
    )


def show_trace_replay_player(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    replay_rows = puzzle.build_trace_replay(result, heuristic, limit=80)
    if not replay_rows:
        st.info("Trace capture is disabled." if lang == "en" else "Trace đang bị tắt.")
        return

    story_rows = puzzle.build_trace_story(result, heuristic)
    replay_index = st.slider(
        text(lang, "trace_replay_row"),
        min_value=0,
        max_value=len(replay_rows) - 1,
        value=0,
    )
    row = replay_rows[replay_index]
    story = story_rows[replay_index] if replay_index < len(story_rows) else {}

    st.markdown(
        f"""
        <div class="readiness-grid">
          {readiness_chip(text(lang, "step"), str(row.get("Step", "")), "")}
          {readiness_chip("g(n)", str(row.get("g", "")), "")}
          {readiness_chip("h(n)", str(row.get("h", "")), "")}
          {readiness_chip("f(n)", str(row.get("f", "")), "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        node_states = [puzzle.parse_state(str(row.get("Node", "")))]
    except ValueError:
        node_states = []
    frontier_states = trace_states_from_text(row.get("Frontier After Expansion", ""), limit=4)
    reached_states = trace_states_from_text(row.get("Reached After Expansion", ""), limit=4)
    trace_html = "".join(
        [
            trace_state_panel_html(
                text(lang, "selected_node"),
                text(lang, "node_expansion_subtitle"),
                node_states,
                row.get("Node", ""),
            ),
            trace_state_panel_html(
                text(lang, "frontier_after"),
                text(lang, "frontier_subtitle"),
                frontier_states,
                row.get("Frontier After Expansion", ""),
            ),
            trace_state_panel_html(
                text(lang, "reached_after"),
                text(lang, "reached_subtitle"),
                reached_states,
                row.get("Reached After Expansion", ""),
            ),
        ]
    )
    st.markdown(f'<div class="trace-triptych">{trace_html}</div>', unsafe_allow_html=True)

    detail_html = "".join(
        [
            trace_detail_card(text(lang, "priority_rule"), localize_trace_text(row.get("Priority Rule", ""), lang)),
            trace_detail_card(text(lang, "selection_key"), localize_trace_text(row.get("Selection Key", ""), lang)),
            trace_detail_card(text(lang, "generated_skipped"), f"{row.get('Generated Children', '')} / {row.get('Skipped States', '')}"),
            trace_detail_card(text(lang, "trace_story"), localize_trace_text(story.get("Why This Node", row.get("Decision/Note", "")), lang)),
        ]
    )
    st.markdown(f'<div class="trace-player-grid">{detail_html}</div>', unsafe_allow_html=True)


def search_tree_cards_html(tree: Dict[str, Any], lang: str) -> str:
    cards = []
    for row in tree.get("nodes", [])[:18]:
        badges = []
        if row.get("is_start"):
            badges.append(text(lang, "tree_start"))
        if row.get("is_goal"):
            badges.append(text(lang, "tree_goal"))
        badge_text = " · ".join(badges) if badges else text(lang, "tree_depth", depth=row.get("depth", ""))
        cards.append(
            (
                '<div class="tree-card">'
                '<strong>#{id} {badge}</strong>'
                '<code>{state}</code>'
                '<span>{parent_label}={parent} · {action_label}={action}<br>g={g} · h={h} · f={f}</span>'
                '</div>'
            ).format(
                id=escape(str(row.get("id", ""))),
                badge=escape(badge_text),
                state=escape(str(row.get("state", ""))),
                parent_label=escape(text(lang, "tree_parent")),
                parent=escape(str(row.get("parent", "-") or "-")),
                action_label=escape(text(lang, "tree_action")),
                action=escape(localize_action(str(row.get("action", "")), lang)),
                g=escape(str(row.get("g", ""))),
                h=escape(str(row.get("h", ""))),
                f=escape(str(row.get("f", ""))),
            )
        )
    return f'<div class="tree-card-grid">{"".join(cards)}</div>'


def show_heuristic_inspector(state: puzzle.State, lang: str, heuristic: str) -> None:
    explanation = puzzle.explain_heuristic(state, heuristic)
    st.subheader(text(lang, "heuristic_inspector"))
    st.markdown(f'<p class="section-note">{escape(explanation["admissibility_note"])}</p>', unsafe_allow_html=True)

    total_rows = [{"Metric": key, "Value": value} for key, value in explanation["totals"].items()]
    st.markdown(f"**{text(lang, 'heuristic_totals')}**")
    st.dataframe(localize_table(puzzle._to_table(total_rows), lang), width="stretch", hide_index=True)

    st.markdown(f"**{text(lang, 'tile_contributions')}**")
    st.dataframe(localize_table(puzzle._to_table(explanation["tile_rows"]), lang), width="stretch", hide_index=True)

    if heuristic == "linear_conflict":
        st.markdown(f"**{text(lang, 'linear_conflicts')}**")
        if explanation["linear_conflicts"]:
            st.dataframe(localize_table(puzzle._to_table(explanation["linear_conflicts"]), lang), width="stretch", hide_index=True)
        else:
            st.info(text(lang, "no_linear_conflicts"))


def show_experiment_lab(lang: str, heuristic: str) -> None:
    st.subheader(text(lang, "experiment_lab"))
    st.caption(text(lang, "benchmark_caption"))
    if st.button(text(lang, "run_experiment"), width="stretch", key="run_experiment_lab"):
        with st.spinner("Running experiment suite across presets..." if lang == "en" else "Đang chạy phòng thử nghiệm trên các mẫu..."):
            st.session_state.last_experiment = puzzle.run_experiment_suite(heuristic_name=heuristic)
            st.session_state.last_experiment_heuristic = heuristic

    experiment = st.session_state.get("last_experiment")
    if experiment is not None and experiment.get("heuristic") != heuristic:
        experiment = None
    if experiment is None:
        st.info("Run the experiment to produce a deterministic comparison table." if lang == "en" else "Chạy thử nghiệm để tạo bảng so sánh cố định.")
        return

    st.caption(f"{text(lang, 'heuristic')}: {experiment['heuristic']}")
    st.dataframe(localize_table(puzzle._to_table(experiment["rows"]), lang), width="stretch", hide_index=True)
    experiment_markdown = puzzle.export_experiment_markdown(experiment)
    st.download_button(
        text(lang, "download_experiment"),
        data=experiment_markdown,
        file_name="8_puzzle_experiment_lab.md",
        mime="text/markdown",
        width="stretch",
    )
    st.markdown("**Heuristic dominance: misplaced vs manhattan**" if lang == "en" else "**So sánh độ mạnh heuristic: sai vị trí và Manhattan**")
    dominance = puzzle.run_heuristic_dominance_demo(st.session_state.start_state)
    st.dataframe(localize_table(puzzle._to_table(dominance["rows"]), lang), width="stretch", hide_index=True)
    st.caption(dominance["conclusion"])


def run_demo_benchmark(heuristic: str, lang: str) -> Any:
    rows = []
    config = puzzle.TraceConfig(max_expansions=8000, max_trace_rows=0, ids_max_depth=35, ida_max_iterations=80, seed=7)
    algorithms = ["BFS", "UCS", "A*", "Greedy", "IDA*"]
    for preset_name in ["easy_2", "medium_10", "hard_20"]:
        state = puzzle.DEMO_PRESETS[preset_name]
        for algorithm in algorithms:
            result = puzzle.run_algorithm(state, algorithm, heuristic=heuristic, config=config)
            row = {"Preset": preset_name, "Group": puzzle.ALGORITHM_INFO[result.algorithm]["group"]}
            row.update(result.summary_row())
            rows.append(row)
    return localize_table(puzzle._to_table(rows), lang)


def current_shuffle_note(lang: str) -> str:
    preset_name = st.session_state.get("last_preset_name")
    if preset_name:
        return text(lang, "preset_note", name=preset_name)
    count = st.session_state.shuffle_count
    if count == 0:
        return text(lang, "initial_shuffle")
    return text(
        lang,
        "shuffle_note",
        moves=st.session_state.last_shuffle_moves,
        seed=st.session_state.last_shuffle_seed,
        count=count,
    )


def shuffle_start_state(scramble_moves: int) -> None:
    st.session_state.shuffle_count += 1
    effective_seed = st.session_state.seed + st.session_state.shuffle_count
    st.session_state.start_state = puzzle.generate_random_state(scramble_moves, effective_seed)
    reset_game_state(st.session_state.start_state)
    st.session_state.last_shuffle_moves = scramble_moves
    st.session_state.last_shuffle_seed = effective_seed
    st.session_state.last_result = None
    st.session_state.last_comparison = None
    st.session_state.last_benchmark = None
    st.session_state.last_preset_name = ""
    st.session_state.playback_step = 0


def load_demo_preset(preset_name: str) -> None:
    st.session_state.start_state = puzzle.DEMO_PRESETS[preset_name]
    reset_game_state(st.session_state.start_state)
    st.session_state.last_preset_name = preset_name
    st.session_state.last_result = None
    st.session_state.last_comparison = None
    st.session_state.last_benchmark = None
    st.session_state.playback_step = 0


def reset_game_state(state: puzzle.State | None = None) -> None:
    st.session_state.game_state = state or st.session_state.start_state
    st.session_state.game_moves = 0
    st.session_state.game_history = []
    st.session_state.game_message = ""


def clear_solver_outputs() -> None:
    st.session_state.last_result = None
    st.session_state.last_comparison = None
    st.session_state.last_benchmark = None
    st.session_state.playback_step = 0


def move_game(action: str) -> None:
    legal = dict(puzzle.neighbors(st.session_state.game_state))
    if action not in legal:
        lang = "vi" if st.session_state.get("language_choice") == "Tiếng Việt" else "en"
        st.session_state.game_message = text(lang, "cannot_move", action=localize_action(action, lang))
        return
    previous = st.session_state.game_state
    st.session_state.game_history.append((previous, action))
    st.session_state.game_state = legal[action]
    st.session_state.game_moves += 1
    st.session_state.game_message = ""


def move_tile_in_game(tile: int) -> None:
    for action, next_state in puzzle.neighbors(st.session_state.game_state):
        if next_state.index(0) == st.session_state.game_state.index(tile):
            move_game(action)
            return
    lang = "vi" if st.session_state.get("language_choice") == "Tiếng Việt" else "en"
    st.session_state.game_message = text(lang, "not_adjacent")


def undo_game_move() -> None:
    if not st.session_state.game_history:
        return
    previous, _action = st.session_state.game_history.pop()
    st.session_state.game_state = previous
    st.session_state.game_moves = max(0, st.session_state.game_moves - 1)
    st.session_state.game_message = ""


def show_interactive_game_panel(lang: str) -> None:
    solved = st.session_state.game_state == puzzle.GOAL_STATE
    h_value = puzzle.manhattan_distance(st.session_state.game_state)
    title = text(lang, "game_title")
    subtitle = text(lang, "game_note")
    solved_text = text(lang, "game_solved")
    progress_text = text(lang, "game_progress")
    st.markdown(
        f"""
        <div class="game-panel">
          <h3>{escape(title)}</h3>
          <p class="dpad-note">{escape(subtitle)}</p>
          <div class="game-meta">
            <span class="game-pill">{escape(text(lang, "game_moves"))}: {st.session_state.game_moves}</span>
            <span class="game-pill">h(n): {h_value}</span>
            <span class="game-pill">{escape(solved_text if solved else progress_text)}</span>
          </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.game_image_url:
        st.markdown(image_board_html(st.session_state.game_state, st.session_state.game_image_url, lang), unsafe_allow_html=True)
        st.caption(text(lang, "click_tile_hint"))
    playable_tile_grid(st.session_state.game_state, lang)

    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button(text(lang, "undo"), key="game_undo", disabled=not st.session_state.game_history, width="stretch"):
            undo_game_move()
            st.rerun()
    with action_cols[1]:
        if st.button(text(lang, "reset_game"), key="game_reset", width="stretch"):
            reset_game_state()
            st.rerun()
    if st.button(text(lang, "use_as_start"), key="game_use_start", width="stretch"):
        st.session_state.start_state = st.session_state.game_state
        clear_solver_outputs()
        st.session_state.last_preset_name = ""
        st.rerun()
    if st.session_state.game_message:
        st.caption(st.session_state.game_message)
    st.markdown("</div>", unsafe_allow_html=True)


def show_result(result: puzzle.SearchResult, lang: str, heuristic: str) -> None:
    validation = puzzle.validate_result(result, heuristic)
    summary_tab, trace_tab, heuristics_tab, experiment_tab, report_tab = st.tabs(
        [
            text(lang, "summary_tab"),
            text(lang, "academic_trace_tab"),
            text(lang, "heuristics_tab"),
            text(lang, "experiment_tab"),
            text(lang, "report_tab"),
        ]
    )

    with summary_tab:
        st.subheader(text(lang, "run_summary"))
        st.markdown(metric_cards_html(result, lang), unsafe_allow_html=True)
        st.subheader(text(lang, "algorithm_certificate"))
        st.markdown(certificate_chips_html(validation, lang), unsafe_allow_html=True)
        with st.expander(text(lang, "grading_checklist"), expanded=False):
            show_grading_checklist(lang)
        with st.expander(text(lang, "result_details"), expanded=False):
            st.dataframe(certificate_rows(validation, lang), width="stretch", hide_index=True)
            st.dataframe(localize_table(puzzle._to_table([result.summary_row()]), lang), width="stretch")

        st.markdown(f"**{text(lang, 'coursework_report')}**")
        st.caption(puzzle.academic_conclusion(result))

        goal_col, final_col = st.columns(2)
        with goal_col:
            show_goal_panel(lang)
        with final_col:
            if result.path:
                show_board(text(lang, "final_state"), result.path[-1], lang, "goal_board")
            else:
                show_board(text(lang, "best_final_state"), result.start, lang)

        with st.expander(text(lang, "path_playback"), expanded=bool(result.found and len(result.path) <= 8)):
            show_path_player(result, lang, heuristic)

    with trace_tab:
        show_trace_story(result, lang, heuristic)
        st.subheader(text(lang, "trace_player"))
        show_trace_replay_player(result, lang, heuristic)
        st.subheader(text(lang, "search_tree_preview"))
        tree = puzzle.build_search_tree_preview(result.start, heuristic, max_depth=2, max_nodes=25)
        st.markdown(search_tree_cards_html(tree, lang), unsafe_allow_html=True)
        tree_rows = [
            {**row, "parent": "-" if row.get("parent", "") == "" else str(row.get("parent", ""))}
            for row in tree["nodes"]
        ]
        st.dataframe(localize_table(puzzle._to_table(tree_rows), lang), width="stretch", hide_index=True)
        st.subheader(text(lang, "trace"))
        st.dataframe(localize_table(puzzle.render_trace_table(result), lang), width="stretch")
        with st.expander(text(lang, "trace_glossary"), expanded=False):
            st.dataframe(trace_glossary_rows(lang), width="stretch", hide_index=True)
        with st.expander(text(lang, "algorithm_profile"), expanded=False):
            show_algorithm_profile(lang, result.algorithm)

    with heuristics_tab:
        show_heuristic_inspector(result.start, lang, heuristic)
        if result.path:
            with st.expander(text(lang, "final_state"), expanded=False):
                show_heuristic_inspector(result.path[-1], lang, heuristic)

    with experiment_tab:
        show_experiment_lab(lang, heuristic)

    with report_tab:
        experiment = st.session_state.get("last_experiment")
        if experiment is not None and experiment.get("heuristic") != heuristic:
            experiment = None
        report_markdown = puzzle.export_run_markdown(result, heuristic, validation, experiment)
        st.download_button(
            text(lang, "download_report"),
            data=report_markdown,
            file_name=f"8_puzzle_{result.algorithm.replace('*', 'star').replace(' ', '_')}.md",
            mime="text/markdown",
            width="stretch",
        )
        pack_key = f"{result.algorithm}|{heuristic}|{result.start}|{result.path_cost}"
        if st.button(text(lang, "generate_pack"), width="stretch", key="generate_submission_pack"):
            with st.spinner("Generating submission pack (DOCX, PDF, HTML, CSV)..." if lang == "en" else "Đang tạo gói nộp bài (DOCX, PDF, HTML, CSV)..."):
                st.session_state.last_submission_pack = puzzle.build_submission_pack(result, heuristic, validation, experiment)
                st.session_state.last_submission_pack_key = pack_key
        pack = st.session_state.get("last_submission_pack")
        if pack is not None and st.session_state.get("last_submission_pack_key") == pack_key:
            st.download_button(text(lang, "download_docx"), data=pack["docx"], file_name="8_puzzle_coursework_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch")
            st.download_button(text(lang, "download_pdf"), data=pack["pdf"], file_name="8_puzzle_coursework_report.pdf", mime="application/pdf", width="stretch")
            st.download_button(text(lang, "download_html"), data=pack["html"], file_name="8_puzzle_coursework_report.html", mime="text/html", width="stretch")
            st.download_button(text(lang, "download_csv"), data=pack["benchmark_csv"], file_name="8_puzzle_benchmark.csv", mime="text/csv", width="stretch")
        with st.expander(text(lang, "grading_checklist"), expanded=False):
            show_grading_checklist(lang)
        st.text_area(text(lang, "report_preview"), value=report_markdown, height=420)

