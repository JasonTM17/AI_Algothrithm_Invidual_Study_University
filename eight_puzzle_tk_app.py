"""Desktop Tkinter launcher for the 8-Puzzle search visualizer.

Usage:
    python eight_puzzle_tk_app.py            # launch GUI
    python eight_puzzle_tk_app.py --self-test # smoke test (no GUI, no display needed)
"""

from __future__ import annotations

import argparse
import sys


def self_test() -> int:
    """Verify i18n keys resolve and the App constructs without a mainloop."""
    from eight_puzzle_tk import i18n
    assert i18n.t("app_title", "vi"), "vi title missing"
    assert i18n.t("app_title", "en"), "en title missing"

    try:
        import tkinter as tk
        from eight_puzzle_tk.app import App
    except ImportError as e:
        print(f"tkinter not available: {e}")
        return 1

    root = tk.Tk()
    root.withdraw()
    try:
        App(root)
    finally:
        root.destroy()

    print("Tkinter self-test passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="8-Puzzle desktop visualizer (Tkinter).")
    parser.add_argument("--self-test", action="store_true", help="Run smoke test, do not launch GUI.")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    from eight_puzzle_tk.app import run
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
