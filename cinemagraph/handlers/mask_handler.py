"""Mask paint handler — brush strokes become mask polygons."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QLabel

from cinemagraph.config.schema import AppConfig


class MaskHandler:
    def __init__(self, canvas: QLabel, cfg: AppConfig) -> None:
        self._canvas = canvas
        self._cfg = cfg
        self._still_path: Path | None = None
        self._polygons: list[list[tuple[float, float]]] = []

    def load_still(self, path: str) -> None:
        self._still_path = Path(path)
        self._canvas.setText(f"Loaded: {self._still_path.name}")

    def commit_polygon(self, poly: list[tuple[float, float]]) -> None:
        self._polygons.append(poly)

    def export_json(self, target: Path) -> None:
        import json
        target.write_text(
            json.dumps({"polygons": self._polygons, "feather_px": self._cfg.motion.mask_feather_px}),
            encoding="utf-8",
        )