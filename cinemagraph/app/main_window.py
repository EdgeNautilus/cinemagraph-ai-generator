"""Main Qt window — canvas, mask timeline, and pipeline controls."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cinemagraph.config.schema import AppConfig
from cinemagraph.handlers.render_handler import RenderHandler
from cinemagraph.handlers.mask_handler import MaskHandler


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self.setWindowTitle("cinemagraph-ai-generator")
        self.resize(1440, 900)

        self._canvas = QLabel("Drop a still to begin.")
        self._canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._canvas.setMinimumSize(960, 540)

        self._mask_handler = MaskHandler(self._canvas, config)
        self._render_handler = RenderHandler(config)

        open_btn = QPushButton("Open still…")
        open_btn.clicked.connect(self._on_open)
        render_btn = QPushButton("Render loop")
        render_btn.clicked.connect(self._render_handler.run)

        side = QWidget()
        side_layout = QVBoxLayout(side)
        side_layout.addWidget(open_btn)
        side_layout.addWidget(render_btn)
        side_layout.addStretch(1)

        dock = QDockWidget("Pipeline", self)
        dock.setWidget(side)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self.setCentralWidget(self._canvas)

    def _on_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open still", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self._mask_handler.load_still(path)