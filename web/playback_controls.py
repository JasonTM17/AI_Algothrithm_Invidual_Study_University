"""Reusable Streamlit controls for deterministic step-by-step playback."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st


SPEED_SECONDS = (0.25, 0.5, 1.0, 2.0)


def reset_playback_state(*prefixes: str) -> None:
    """Reset independent players when a new puzzle or result is selected."""

    for prefix in prefixes:
        st.session_state[f"{prefix}_step"] = 0
        st.session_state[f"{prefix}_playing"] = False


def _ensure_state(prefix: str, max_step: int) -> tuple[str, str, str]:
    step_key = f"{prefix}_step"
    playing_key = f"{prefix}_playing"
    speed_key = f"{prefix}_speed"
    st.session_state.setdefault(step_key, 0)
    st.session_state.setdefault(playing_key, False)
    st.session_state.setdefault(speed_key, 0.5)
    st.session_state[step_key] = max(0, min(int(st.session_state[step_key]), max_step))
    if max_step == 0:
        st.session_state[playing_key] = False
    return step_key, playing_key, speed_key


def _set_step(step_key: str, playing_key: str, step: int, max_step: int) -> None:
    st.session_state[step_key] = max(0, min(step, max_step))
    st.session_state[playing_key] = False


def render_step_player(
    *,
    prefix: str,
    max_step: int,
    labels: dict[str, str],
    render_frame: Callable[[int], Any],
) -> None:
    """Render manual controls plus non-blocking fragment-based autoplay."""

    step_key, playing_key, speed_key = _ensure_state(prefix, max_step)
    run_every = float(st.session_state[speed_key]) if st.session_state[playing_key] else None

    @st.fragment(run_every=run_every)
    def player_fragment() -> None:
        current_step = max(0, min(int(st.session_state[step_key]), max_step))
        is_playing = bool(st.session_state[playing_key])

        if is_playing:
            current_step = min(current_step + 1, max_step)
            st.session_state[step_key] = current_step
            if current_step >= max_step:
                st.session_state[playing_key] = False
                st.rerun()

        controls = st.columns([1, 1, 1.2, 1, 1.4])
        with controls[0]:
            st.button(
                labels["previous"],
                key=f"{prefix}_previous",
                disabled=is_playing or current_step <= 0,
                on_click=_set_step,
                args=(step_key, playing_key, current_step - 1, max_step),
                width="stretch",
            )
        with controls[1]:
            st.button(
                labels["next"],
                key=f"{prefix}_next",
                disabled=is_playing or current_step >= max_step,
                on_click=_set_step,
                args=(step_key, playing_key, current_step + 1, max_step),
                width="stretch",
            )
        with controls[2]:
            if is_playing:
                if st.button(labels["pause"], key=f"{prefix}_pause", width="stretch"):
                    st.session_state[playing_key] = False
                    st.rerun()
            elif st.button(
                labels["play"],
                key=f"{prefix}_play",
                disabled=current_step >= max_step,
                type="primary",
                width="stretch",
            ):
                st.session_state[playing_key] = True
                st.rerun()
        with controls[3]:
            st.button(
                labels["reset"],
                key=f"{prefix}_reset",
                disabled=is_playing or current_step == 0,
                on_click=_set_step,
                args=(step_key, playing_key, 0, max_step),
                width="stretch",
            )
        with controls[4]:
            st.selectbox(
                labels["speed"],
                SPEED_SECONDS,
                key=speed_key,
                disabled=is_playing,
                format_func=lambda seconds: labels["seconds"].format(seconds=seconds),
                label_visibility="collapsed",
            )

        selected_step = st.slider(
            labels["slider"],
            min_value=0,
            max_value=max_step,
            key=step_key,
            disabled=is_playing,
        )
        render_frame(int(selected_step))

    player_fragment()
