"""Render button handler — runs the full pipeline off the UI thread."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from cinemagraph.config.schema import AppConfig
from cinemagraph.services.export import ExportFormat, export_loop
from cinemagraph.services.pipeline import render_cinemagraph


class _Worker(QObject):
    done = Signal(Path)
    failed = Signal(str)

    def __init__(self, still: Path, cfg: AppConfig) -> None:
        super().__init__()
        self._still = still
        self._cfg = cfg

    def run(self) -> None:
        try:
            from cinemagraph.motion.mask import MaskSpec
            result = render_cinemagraph(self._still, MaskSpec.auto("portrait-soft"), self._cfg)
            out = self._still.with_suffix(".loop.webm")
            export_loop(result, out, ExportFormat.WEBM)
            self.done.emit(out)
        except Exception as exc:  # noqa: BLE001 — surfaced to UI
            self.failed.emit(str(exc))


class RenderHandler(QObject):
    def __init__(self, cfg: AppConfig) -> None:
        super().__init__()
        self._cfg = cfg
        self._thread: QThread | None = None

    def run(self) -> None:
        if self._thread and self._thread.isRunning():
            return
        self._thread = QThread()
        worker = _Worker(Path("input.png"), self._cfg)
        worker.moveToThread(self._thread)
        self._thread.started.connect(worker.run)
        worker.done.connect(lambda p: self._thread.quit())
        worker.failed.connect(lambda msg: self._thread.quit())
        self._thread.start()