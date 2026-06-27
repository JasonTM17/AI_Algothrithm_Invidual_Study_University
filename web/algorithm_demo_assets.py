"""Static GIF lookup and Streamlit renderer for algorithm demonstrations."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

import streamlit as st

from web.ui_text import text


ASSET_DIR = Path(__file__).resolve().parent / "assets" / "algorithm-demos"


def algorithm_demo_slug(algorithm: str) -> str:
    normalized = algorithm.lower().replace("*", " star ")
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def algorithm_demo_path(algorithm: str) -> Path:
    return ASSET_DIR / f"{algorithm_demo_slug(algorithm)}.gif"


def show_algorithm_demo(algorithm: str, lang: str) -> None:
    path = algorithm_demo_path(algorithm)
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="algorithm-demo-heading">
              <span>{escape(text(lang, "algorithm_demo_gif"))}</span>
              <strong>{escape(algorithm)}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not path.is_file():
            st.info(text(lang, "algorithm_demo_missing"))
            return
        st.image(
            str(path),
            caption=text(lang, "algorithm_demo_caption", algorithm=algorithm),
            width="stretch",
        )
