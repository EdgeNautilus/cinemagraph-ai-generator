"""Motion mask specification — which pixels are allowed to move."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from cinemagraph.utils.image_io import feather_alpha


@dataclass(slots=True)
class MaskSpec:
    """Region-of-motion spec.

    `polygons` are normalized [0,1] polygons. `auto_preset` selects a
    heuristic mask (face/hands for portraits, sky for landscapes).
    """
    polygons: list[list[tuple[float, float]]] = field(default_factory=list)
    auto_preset: str | None = None
    feather_px: int = 6

    @classmethod
    def auto(cls, preset: str) -> "MaskSpec":
        return cls(auto_preset=preset)

    @classmethod
    def from_json(cls, path: Path) -> "MaskSpec":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            polygons=[list(map(tuple, poly)) for poly in data.get("polygons", [])],
            auto_preset=data.get("auto_preset"),
            feather_px=int(data.get("feather_px", 6)),
        )

    def rasterize(self, shape: tuple[int, int]) -> np.ndarray:
        h, w = shape
        canvas = np.zeros((h, w), dtype=np.uint8)
        if self.auto_preset:
            canvas = _preset_heuristic(self.auto_preset, h, w)
        for poly in self.polygons:
            pts = np.array([(int(x * w), int(y * h)) for x, y in poly], dtype=np.int32)
            canvas = np.maximum(canvas, _fill_poly(h, w, pts))
        return feather_alpha(canvas, self.feather_px)


def _fill_poly(h: int, w: int, pts: np.ndarray) -> np.ndarray:
    import cv2
    canvas = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(canvas, [pts], 255)
    return canvas


def _preset_heuristic(preset: str, h: int, w: int) -> np.ndarray:
    canvas = np.zeros((h, w), dtype=np.uint8)
    if preset.startswith("portrait"):
        y0, y1 = int(h * 0.15), int(h * 0.85)
        x0, x1 = int(w * 0.20), int(w * 0.80)
        canvas[y0:y1, x0:x1] = 255
    elif preset.startswith("landscape"):
        canvas[: int(h * 0.45), :] = 255
    return canvas