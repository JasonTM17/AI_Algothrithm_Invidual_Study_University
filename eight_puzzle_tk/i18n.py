"""Bilingual (Vietnamese + English) translation strings for the Tkinter app.

The dict grows as features are added in later commits. ``t()`` looks up a key in
the requested language, falls back to English, and finally to the key itself so
missing translations are obvious in the UI.
"""

from __future__ import annotations

from typing import Dict

TEXT: Dict[str, Dict[str, str]] = {
    "vi": {
        # Window + global
        "app_title": "Trực quan hóa thuật toán 8-Puzzle",
        "language": "Ngôn ngữ",
        "lang_vi": "Tiếng Việt",
        "lang_en": "English",
        # Sidebar sections
        "section_controls": "Điều khiển",
        "section_matrix": "Ma trận",
        "section_algorithm": "Thuật toán",
        "section_heuristic": "Heuristic",
        "section_limits": "Giới hạn",
        # Preset + shuffle
        "preset": "Preset demo",
        "preset_custom": "Tùy chỉnh",
        "scramble_moves": "Số bước tự trộn",
        "seed": "Seed (để trống = ngẫu nhiên)",
        "shuffle": "Tự trộn ma trận",
        # Matrix labels
        "start_state": "Trạng thái bắt đầu (Start)",
        "goal_state": "Trạng thái đích (Goal)",
        "copy_start_to_goal": "Sao chép Start → Goal",
        "apply_state": "Áp dụng",
        "state_invalid": "Trạng thái không hợp lệ (cần đủ 0–8, mỗi số đúng 1 lần)",
        # Algorithm
        "algorithm_group": "Nhóm thuật toán",
        "algorithm": "Thuật toán",
        "heuristic": "Heuristic h(n)",
        "use_heuristic": "Dùng heuristic",
        # Limits (TraceConfig keys reused as i18n keys for sidebar labels)
        "max_expansions": "Giới hạn mở rộng node",
        "dfs_depth_limit": "Giới hạn độ sâu DFS",
        "ids_max_depth": "Độ sâu tối đa IDS",
        "ida_max_iterations": "Số vòng tối đa IDA*",
        "local_max_steps": "Số bước tối đa local search",
        "random_restarts": "Số lần restart",
        # Action buttons
        "run": "Chạy thuật toán đã chọn",
        "compare_all": "So sánh tất cả thuật toán",
        "reset": "Đặt lại mặc định",
        # Tabs (used by Notebook)
        "tab_summary": "Tóm tắt",
        "tab_trace": "Trace",
        "tab_heuristics": "Heuristics",
        "tab_experiment": "Experiment",
        "tab_report": "Report",
        # Placeholder
        "coming_soon": "(sẽ thêm ở commit tiếp theo)",
    },
    "en": {
        "app_title": "8-Puzzle Search Visualizer",
        "language": "Language",
        "lang_vi": "Vietnamese",
        "lang_en": "English",
        "section_controls": "Controls",
        "section_matrix": "Matrix",
        "section_algorithm": "Algorithm",
        "section_heuristic": "Heuristic",
        "section_limits": "Limits",
        "preset": "Demo preset",
        "preset_custom": "Custom",
        "scramble_moves": "Scramble moves",
        "seed": "Seed (empty = random)",
        "shuffle": "Shuffle matrix",
        "start_state": "Start state",
        "goal_state": "Goal state",
        "copy_start_to_goal": "Copy Start → Goal",
        "apply_state": "Apply",
        "state_invalid": "Invalid state (need 0–8, each exactly once)",
        "algorithm_group": "Algorithm group",
        "algorithm": "Algorithm",
        "heuristic": "Heuristic h(n)",
        "use_heuristic": "Use heuristic",
        "max_expansions": "Max node expansions",
        "dfs_depth_limit": "DFS depth limit",
        "ids_max_depth": "IDS max depth",
        "ida_max_iterations": "IDA* max iterations",
        "local_max_steps": "Local search max steps",
        "random_restarts": "Random restarts",
        "run": "Run selected algorithm",
        "compare_all": "Compare all algorithms",
        "reset": "Reset to defaults",
        "tab_summary": "Summary",
        "tab_trace": "Trace",
        "tab_heuristics": "Heuristics",
        "tab_experiment": "Experiment",
        "tab_report": "Report",
        "coming_soon": "(coming in next commit)",
    },
}

DEFAULT_LANG = "vi"


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Return the translated string for ``key`` in ``lang``."""
    return TEXT.get(lang, {}).get(key) or TEXT["en"].get(key, key)
