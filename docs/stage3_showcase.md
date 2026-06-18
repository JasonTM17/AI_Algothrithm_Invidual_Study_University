# Stage 3 Showcase

Stage 3 turns the project from a coursework solver into a portfolio-style demo.
The new app is additive and does not replace the existing Streamlit or Tkinter apps.

## Entry point

```bash
python -m pip install -r requirements.txt
python -m streamlit run stage3_search_showcase_app.py
```

## Features

### 1. Search Tree Visualization

The app renders a bounded Graphviz search tree for the selected Start state.

- Uses BFS-style discovery so the tree is easy to explain.
- Displays each board as a 3x3 node.
- Shows `h(n)` beside each state.
- Highlights the A* solution path in bold when A* finds a solution.
- Provides a `.dot` download for reports or slides.

This is intentionally bounded by depth and node count to keep demos responsive.

### 2. Explain Step-by-Step

The app reuses the existing trace system and converts each trace row into a student-friendly explanation.

For each selected trace row, the page shows:

- Node currently selected.
- `g(n)`, `h(n)`, and `f(n)`.
- Priority rule.
- Selection key.
- Frontier preview.
- Reached preview.
- Explanation for why that node was selected.

This is useful for viva/demo questions such as: "Why did A* choose this node?"

### 3. Solution Player

When the selected algorithm finds a solution, the app provides a step slider to replay the path.

For each step, it shows:

- Board state.
- Action just applied.
- Current `g(n)`, `h(n)`, and `f(n)`.
- Next action, if available.

### 4. BFS vs A* Mode

This tab compares BFS and A* on the same Start state and heuristic configuration.

The comparison table includes:

- Found / not found.
- Path cost.
- Expanded nodes.
- Generated nodes.
- Reached states.
- Max frontier.
- Runtime in milliseconds.
- Completeness and optimality notes.

A small bar chart makes it easier to present why heuristic search can reduce search effort.

### 5. Deploy and Release Readiness

The repository now includes:

- `Dockerfile` for containerized Streamlit deployment.
- `.streamlit/config.toml` for Streamlit server defaults.
- `render.yaml` for Render-style web deployment.
- `.github/workflows/release-desktop.yml` for building and publishing a Windows `.exe`.

## Recommended demo script

1. Open `stage3_search_showcase_app.py`.
2. Select `easy_2` or `medium_10`.
3. Show the Search Tree tab and explain Start, Goal, neighbors, and heuristic values.
4. Open Explain Step-by-Step and choose A*.
5. Move the trace slider and explain `f(n)=g(n)+h(n)`.
6. Open Solution Player and replay the path.
7. Open BFS vs A* and compare expanded/generated nodes.
8. End with Deploy & Release to show professional engineering readiness.
