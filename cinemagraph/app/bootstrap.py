"""Qt application bootstrap for the desktop GUI.

Creates the QApplication, applies the dark theme, wires the main window,
and installs a global exception hook so pipeline crashes surface as a
dialog instead of a silent exit.
"""

from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from cinemagraph.app.main_window import MainWindow
from cinemagraph.config.loader import load_config
from cinemagraph.utils.logging import configure_logging


def _install_excepthook() -> None:
    def _hook(exc_type, exc, tb):  # type: ignore[no-untyped-def]
        msg = "".join(traceback.format_exception(exc_type, exc, tb))
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("cinemagraph-ai-generator — crash")
        box.setText(str(exc))
        box.setDetailedText(msg)
        box.exec()

    sys.excepthook = _hook


def run() -> int:
    configure_logging()
    _install_excepthook()
    app = QApplication(sys.argv)
    app.setApplicationName("cinemagraph-ai-generator")
    app.setOrganizationName("cinemagraph-ai-generator")

    config = load_config()
    window = MainWindow(config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())