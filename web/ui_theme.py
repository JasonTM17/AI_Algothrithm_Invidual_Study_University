"""Theme CSS injection for 8-Puzzle UI."""

import os
import streamlit as st

_MINIMAL_FALLBACK_CSS = """
:root {
  --surface: var(--background-color, #f7f5f2);
  --panel: var(--secondary-background-color, #faf8f5);
  --ink: var(--text-color, #1e1b18);
  --accent: var(--primary-color, #0d9488);
  --line: rgba(30, 27, 24, 0.12);
}
.puzzle-board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.tile { padding: 12px; text-align: center; border: 1px solid var(--line); border-radius: 8px; }
"""


def apply_theme() -> None:
    """Inject shared design token CSS from external file."""
    css_path = os.path.join(os.path.dirname(__file__), 'ui-theme.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as _f:
            css = _f.read()
    except FileNotFoundError:
        css = _MINIMAL_FALLBACK_CSS
    st.markdown('<style>\n' + css + '\n</style>', unsafe_allow_html=True)
