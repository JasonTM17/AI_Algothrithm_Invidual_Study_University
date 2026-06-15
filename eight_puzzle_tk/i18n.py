"""Bilingual (Vietnamese + English) translation strings for the Tkinter app.

The dict grows as features are added in later commits. ``t()`` looks up a key in
the requested language, falls back to English, and finally to the key itself so
missing translations are obvious in the UI.
"""

from __future__ import annotations

from typing import Dict

TEXT: Dict[str, Dict[str, str]] = {
    "vi": {
        "app_title": "Trực quan hóa thuật toán 8-Puzzle",
        "language": "Ngôn ngữ",
        "lang_vi": "Tiếng Việt",
        "lang_en": "English",
        "section_controls": "Điều khiển",
        "coming_soon": "(sẽ thêm ở commit tiếp theo)",
    },
    "en": {
        "app_title": "8-Puzzle Search Visualizer",
        "language": "Language",
        "lang_vi": "Vietnamese",
        "lang_en": "English",
        "section_controls": "Controls",
        "coming_soon": "(coming in the next commit)",
    },
}

DEFAULT_LANG = "vi"


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Return the translated string for ``key`` in ``lang``."""
    return TEXT.get(lang, {}).get(key) or TEXT["en"].get(key, key)
