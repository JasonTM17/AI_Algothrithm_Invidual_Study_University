"""Stage 3 showcase UI for the 8-Puzzle Search Lab.

This app is intentionally additive: it reuses the existing core engine from
`src/eight_puzzle_search_app.py` and gives the project a portfolio-style demo page
with search-tree visualization, step-by-step explanation, and BFS vs A*
comparison.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import sys
from typing import Any, Dict, List, Sequence, Set, Tuple

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import eight_puzzle_search_app as puzzle


State = Tuple[int, ...]


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _board_label(state: State, h_value: int, index: int) -> str:
    return f"#{index} | h={h_value}\n{puzzle.board_string(state)}"


def _parse_sidebar_state() -> State:
    preset_names = list(puzzle.DEMO_PRESETS.keys())
    preset = st.sidebar.selectbox("Preset", preset_names + ["custom"], index=0)
    if preset == "custom":
        raw = st.sidebar.text_input(
            "Custom Start",
            value="1 2 3 4 5 6 0 7 8",
            help="Nhập 9 số 0..8, ví dụ: 1 2 3 4 5 6 0 7 8",
        )
        return puzzle.parse_state(raw)
    return puzzle.DEMO_PRESETS[preset]


def _metric_rows(results: Sequence[puzzle.SearchResult]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for result in results:
        rows.append(
            {
                "Algorithm": result.algorithm,
                "Found": result.found,
                "Path Cost": "" if result.path_cost is None else result.path_cost,
                "Expanded": result.expanded,
                "Generated": result.generated,
                "Reached": result.reached_count,
                "Max Frontier": result.max_frontier,
                "Runtime ms": round(result.runtime_ms, 3),
                "Trace Rows": len(result.trace_rows),
                "Optimal": result.optimal,
                "Complete": result.complete,
            }
        )
    return rows


def build_search_tree_dot(
    start: State,
    goal: State,
    heuristic_name: str,
    max_depth: int,
    max_nodes: int,
) -> Tuple[str, Dict[str, Any]]:
    """Build a bounded DOT graph for the discovered state tree.

    The graph is deliberately bounded so the Streamlit page stays responsive.
    It visualizes the first BFS-style discovery tree and highlights the A* path
    when A* finds one under the same limits.
    """

    heuristic = puzzle.get_heuristic(heuristic_name, goal)
    result = puzzle.run_algorithm(
        start,
        "A*",
        heuristic=heuristic_name,
        goal=goal,
        config=puzzle.TraceConfig(max_expansions=5000, max_trace_rows=0),
    )
    solution_path: Set[State] = set(result.path)

    node_ids: Dict[State, int] = {start: 0}
    depths: Dict[State, int] = {start: 0}
    edges: List[Tuple[State, State, str]] = []
    queue = deque([start])
    skipped_duplicates = 0

    if not puzzle.is_solvable(start, goal):
        label = _dot_escape(_board_label(start, heuristic(start), 0))
        dot = "digraph SearchTree {\n  rankdir=TB;\n  node [shape=box, fontname=\"Consolas\"];\n"
        dot += f"  n0 [label=\"{label}\", peripheries=2];\n"
        dot += "}\n"
        return dot, {
            "nodes": 1,
            "edges": 0,
            "skipped_duplicates": 0,
            "solution_found": False,
            "note": "Start state is unsolvable, so the search tree is intentionally not expanded.",
        }

    while queue and len(node_ids) < max_nodes:
        state = queue.popleft()
        depth = depths[state]
        if depth >= max_depth or state == goal:
            continue
        for action, next_state in puzzle.neighbors(state):
            if next_state in node_ids:
                skipped_duplicates += 1
                continue
            node_ids[next_state] = len(node_ids)
            depths[next_state] = depth + 1
            edges.append((state, next_state, action))
            queue.append(next_state)
            if len(node_ids) >= max_nodes:
                break

    lines = [
        "digraph SearchTree {",
        "  rankdir=TB;",
        "  node [shape=box, fontname=\"Consolas\", style=\"rounded\"];",
        "  edge [fontname=\"Consolas\"];",
    ]
    for state, node_id in node_ids.items():
        label = _dot_escape(_board_label(state, heuristic(state), node_id))
        attrs = [f'label="{label}"']
        if state == goal:
            attrs.append("peripheries=2")
        if state in solution_path:
            attrs.append('style="rounded,bold"')
        lines.append(f"  n{node_id} [{', '.join(attrs)}];")
    for parent, child, action in edges:
        lines.append(f"  n{node_ids[parent]} -> n{node_ids[child]} [label=\"{action}\"];")
    lines.append("}")

    return "\n".join(lines), {
        "nodes": len(node_ids),
        "edges": len(edges),
        "skipped_duplicates": skipped_duplicates,
        "solution_found": result.found,
        "solution_cost": result.path_cost,
        "note": "Bold nodes are on the A* solution path when a solution is available.",
    }


def render_state_card(title: str, state: State) -> None:
    st.markdown(f"**{title}**")
    st.code(puzzle.board_string(state), language="text")


def render_explain_step(result: puzzle.SearchResult, heuristic_name: str) -> None:
    story_rows = puzzle.build_trace_story(result, heuristic_name)
    if not story_rows:
        st.info("Trace đang rỗng. Hãy tăng `Max trace rows` hoặc chọn thuật toán có trace chi tiết hơn.")
        return

    selected_index = st.slider(
        "Trace step",
        min_value=0,
        max_value=len(story_rows) - 1,
        value=0,
        help="Chọn một dòng trace để xem vì sao node đó được thuật toán chọn.",
    )
    trace_row = result.trace_rows[selected_index]
    story_row = story_rows[selected_index]

    col_node, col_reason = st.columns([1, 1])
    with col_node:
        st.markdown("### Node đang xét")
        st.code(str(trace_row.get("Node", "")), language="text")
        st.metric("g(n)", trace_row.get("g", ""))
        st.metric("h(n)", trace_row.get("h", ""))
        st.metric("f(n)", trace_row.get("f", ""))
    with col_reason:
        st.markdown("### Giải thích quyết định")
        st.write(story_row.get("Why This Node", ""))
        st.markdown("**Priority rule**")
        st.write(trace_row.get("Priority Rule", ""))
        st.markdown("**Selection key**")
        st.code(str(trace_row.get("Selection Key", "")), language="text")

    with st.expander("Frontier / Reached sau bước này", expanded=False):
        left, right = st.columns(2)
        with left:
            st.markdown("**Frontier preview**")
            st.code(str(trace_row.get("Frontier", "")), language="text")
        with right:
            st.markdown("**Reached preview**")
            st.code(str(trace_row.get("Reached", "")), language="text")

    with st.expander("Bảng trace đầy đủ", expanded=False):
        st.dataframe(puzzle.render_trace_table(result), use_container_width=True)


def render_solution_player(result: puzzle.SearchResult, heuristic_name: str) -> None:
    if not result.found or not result.path:
        st.info("Thuật toán chưa tìm được lời giải trong giới hạn hiện tại.")
        return
    heuristic = puzzle.get_heuristic(heuristic_name, result.goal)
    step = st.slider("Solution step", 0, len(result.path) - 1, 0)
    state = result.path[step]
    action = "Start" if step == 0 else result.actions[step - 1]
    col_board, col_info = st.columns([1, 1])
    with col_board:
        render_state_card(f"Step {step}", state)
    with col_info:
        st.metric("Action", action)
        st.metric("g(n)", step)
        st.metric("h(n)", heuristic(state))
        st.metric("f(n)", step + heuristic(state))
        if step + 1 < len(result.path):
            st.write(f"Next action: `{result.actions[step]}`")
        else:
            st.success("Đã tới Goal.")


def main() -> None:
    st.set_page_config(page_title="8-Puzzle Stage 3 Showcase", layout="wide")
    st.title("8-Puzzle Search Lab - Stage 3 Showcase")
    st.caption(
        "Portfolio demo: Search tree visualization, explain step-by-step, BFS vs A* comparison, "
        "and deployment/release readiness."
    )

    st.sidebar.header("Run configuration")
    try:
        start = _parse_sidebar_state()
    except Exception as exc:
        st.sidebar.error(f"Start state không hợp lệ: {exc}")
        st.stop()

    goal = puzzle.GOAL_STATE
    heuristic_name = st.sidebar.selectbox("Heuristic", puzzle.DEFAULT_HEURISTICS, index=1)
    max_expansions = st.sidebar.slider("Max expansions", 100, 20000, 5000, step=100)
    max_trace_rows = st.sidebar.slider("Max trace rows", 10, 500, 120, step=10)
    tree_depth = st.sidebar.slider("Tree depth", 1, 8, 4)
    tree_nodes = st.sidebar.slider("Tree node limit", 10, 200, 60, step=10)

    start_col, goal_col, check_col = st.columns([1, 1, 1])
    with start_col:
        render_state_card("Start", start)
    with goal_col:
        render_state_card("Goal", goal)
    with check_col:
        st.metric("Solvable", "Yes" if puzzle.is_solvable(start, goal) else "No")
        st.metric("Misplaced", puzzle.misplaced_tiles(start, goal))
        st.metric("Manhattan", puzzle.manhattan_distance(start, goal))

    tab_tree, tab_explain, tab_compare, tab_release = st.tabs(
        [
            "Search Tree Visualization",
            "Explain Step-by-Step",
            "BFS vs A* Mode",
            "Deploy & Release",
        ]
    )

    with tab_tree:
        st.subheader("Bounded search tree")
        st.write(
            "Cây này dùng BFS-style discovery để dễ nhìn. Nếu A* tìm được nghiệm, các node trên "
            "đường đi A* được in đậm để người xem thấy hướng đi tối ưu."
        )
        dot, meta = build_search_tree_dot(start, goal, heuristic_name, tree_depth, tree_nodes)
        st.graphviz_chart(dot, use_container_width=True)
        st.json(meta)
        st.download_button("Download DOT graph", dot, file_name="8_puzzle_search_tree.dot")

    with tab_explain:
        st.subheader("Why this node?")
        algorithm = st.selectbox("Algorithm to explain", ["BFS", "UCS", "Greedy", "A*", "IDA*"], index=3)
        config = puzzle.TraceConfig(
            max_expansions=max_expansions,
            max_trace_rows=max_trace_rows,
            frontier_preview=4,
            reached_preview=4,
            ids_max_depth=35,
            ida_max_iterations=80,
        )
        result = puzzle.run_algorithm(start, algorithm, heuristic=heuristic_name, config=config, goal=goal)
        st.dataframe(pd.DataFrame(_metric_rows([result])), use_container_width=True)
        render_explain_step(result, heuristic_name)
        st.divider()
        st.subheader("Solution player")
        render_solution_player(result, heuristic_name)

    with tab_compare:
        st.subheader("BFS vs A* comparison")
        compare_config = puzzle.TraceConfig(
            max_expansions=max_expansions,
            max_trace_rows=0,
            ids_max_depth=35,
            ida_max_iterations=80,
        )
        bfs = puzzle.run_algorithm(start, "BFS", heuristic=heuristic_name, config=compare_config, goal=goal)
        astar = puzzle.run_algorithm(start, "A*", heuristic=heuristic_name, config=compare_config, goal=goal)
        rows = _metric_rows([bfs, astar])
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        chart_columns = ["Expanded", "Generated", "Runtime ms"]
        chart_df = df.set_index("Algorithm")[chart_columns]
        st.bar_chart(chart_df)

        st.markdown(
            """
**Cách thuyết trình nhanh:**

- BFS mở rộng theo từng tầng, không dùng heuristic, nên dễ hiểu và tối ưu khi cost mỗi bước bằng 1.
- A* dùng `f(n)=g(n)+h(n)`, vì vậy thường mở ít node hơn khi heuristic tốt.
- Với `manhattan` hoặc `misplaced`, A* có thể trình bày là solver tối ưu cho 8-Puzzle chuẩn nếu không bị giới hạn tài nguyên.
"""
        )
        st.download_button(
            "Download comparison CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="bfs_vs_astar_comparison.csv",
            mime="text/csv",
        )

    with tab_release:
        st.subheader("Deploy web")
        st.markdown(
            """
App này đã sẵn sàng để deploy như một Streamlit app riêng.

```bash
python -m pip install -r requirements.txt
python -m streamlit run src/stage3_search_showcase_app.py
```

Khi deploy lên Streamlit Community Cloud, chọn entry point:

```text
src/stage3_search_showcase_app.py
```
"""
        )
        st.subheader("Release desktop .exe")
        st.markdown(
            """
Workflow `Build Desktop EXE` sẽ build file `.exe` trên Windows runner khi push tag dạng `v*` hoặc chạy thủ công từ tab Actions.

```bash
git tag v1.0.0
git push origin v1.0.0
```

Artifact dự kiến: `8PuzzleSearchLab.exe`.
"""
        )


if __name__ == "__main__":
    main()
