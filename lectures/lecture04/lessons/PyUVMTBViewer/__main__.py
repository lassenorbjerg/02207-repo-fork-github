"""Command-line entry point for the PyUVM testbench viewer."""

from __future__ import annotations

import argparse
import sys

from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="View a PyUVM testbench hierarchy")
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Viewer JSON configuration or top-level PyUVM test file",
    )
    arguments = parser.parse_args(argv)

    application = QApplication(sys.argv[:1])
    window = MainWindow(arguments.input_file)
    window.show()
    return application.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
