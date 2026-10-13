"""Bilinear remap with per-pixel motion gating."""

from __future__ import annotations

import cv2
import numpy as np


def remap_frame(still: np.ndarray, flow: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Warp `still` by `flow`, gated by `mask` (float32 in [0,1])."""
    h, w = still.shape[:2]
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (xs + flow[..., 0]).astype(np.float32)
    map_y = (ys + flow[..., 1]).astype(np.float32)
    warped = cv2.remap(
        still, map_x, map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )
    m = mask[..., None] if mask.ndim == 2 else mask
    return (warped.astype(np.float32) * m + still.astype(np.float32) * (1.0 - m)).astype(np.uint8)